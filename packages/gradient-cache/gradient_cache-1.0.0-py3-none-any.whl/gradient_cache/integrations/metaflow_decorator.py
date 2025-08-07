"""
Metaflow Integration - The User-Friendly Interface

This module provides a simple decorator that Netflix engineers can use
to automatically optimize GPU memory usage in their training workflows.

Example usage:
    @gradient_cache.optimize(compression_ratio=10)
    def train(self):
        # Your normal training code - no changes needed!
        model.train()
"""

import torch
import torch.nn as nn
from functools import wraps
from typing import Optional, Union, Callable, Any
import warnings
import sys
import os

# Import our core components
from ..core.adaptive_compressor import AdaptiveGradientCompressor
from ..core.memory_manager import GPUMemoryManager
from ..core.hook_manager import GradientCacheHookManager


class GradientCacheOptimizer:
    """
    Optimizer wrapper that handles gradient retrieval and application.
    
    This wraps the user's optimizer to seamlessly integrate compressed
    gradients without changing their training code.
    """
    
    def __init__(self, 
                 original_optimizer: torch.optim.Optimizer,
                 hook_manager: GradientCacheHookManager):
        """
        Wrap an existing optimizer with gradient cache support.
        
        Args:
            original_optimizer: The user's original optimizer
            hook_manager: Our hook manager for gradient retrieval
        """
        self.optimizer = original_optimizer
        self.hook_manager = hook_manager
        
        # Preserve original optimizer attributes
        self.__dict__.update(original_optimizer.__dict__)
        
    def step(self, closure: Optional[Callable] = None) -> Optional[float]:
        """
        Perform optimization step with compressed gradients.
        
        This is called instead of the original optimizer.step().
        """
        # Retrieve compressed gradients from CPU
        self.hook_manager.apply_gradients()
        
        # Perform the actual optimization step
        loss = self.optimizer.step(closure)
        
        # Clean up for next iteration
        self.hook_manager.step_completed()
        
        return loss
    
    def zero_grad(self, set_to_none: bool = True) -> None:
        """Forward zero_grad to original optimizer."""
        self.optimizer.zero_grad(set_to_none)
        
    @property
    def param_groups(self):
        """Forward param_groups property."""
        return self.optimizer.param_groups
        
    @property
    def state(self):
        """Forward state property."""
        return self.optimizer.state


class GradientCacheDecorator:
    """
    Main decorator class for Metaflow integration.
    
    This provides the @gradient_cache.optimize() decorator that users
    add to their training steps.
    """
    
    def __init__(self,
                 compression_ratio: float = 10,
                 memory_budget: str = "80%",
                 profile_first: bool = True,
                 async_offload: bool = True,
                 warmup_steps: int = 1000,
                 exclude_layers: Optional[list] = None,
                 verbose: bool = False,
                 checkpoint_frequency: int = 100):
        """
        Initialize the gradient cache decorator.
        
        Args:
            compression_ratio: Target compression (10 = keep 10% of gradients)
            memory_budget: Target GPU memory usage (e.g., "80%")
            profile_first: Profile memory usage before enabling compression
            async_offload: Use asynchronous CPU transfers
            warmup_steps: Steps before full compression
            exclude_layers: Layer patterns to exclude from compression
            verbose: Print compression statistics
            checkpoint_frequency: How often to save compression stats
        """
        self.compression_ratio = compression_ratio
        self.memory_budget = memory_budget
        self.profile_first = profile_first
        self.async_offload = async_offload
        self.warmup_steps = warmup_steps
        self.exclude_layers = exclude_layers or []
        self.verbose = verbose
        self.checkpoint_frequency = checkpoint_frequency
        
    def __call__(self, func: Callable) -> Callable:
        """
        Decorate a Metaflow step function.
        
        This wraps the user's training step with our optimization logic.
        """
        @wraps(func)
        def wrapper(flow_self, *args, **kwargs):
            """
            The wrapped function that runs instead of the original.
            
            Args:
                flow_self: The Metaflow Flow instance
            """
            # Check if GPU is available
            if not torch.cuda.is_available():
                warnings.warn("No GPU available. Gradient cache disabled.")
                return func(flow_self, *args, **kwargs)
            
            # Initialize gradient cache system
            gradient_cache_state = self._initialize_gradient_cache(flow_self)
            
            if gradient_cache_state is None:
                # Couldn't initialize, run normally
                return func(flow_self, *args, **kwargs)
            
            try:
                # Run the actual training step
                result = func(flow_self, *args, **kwargs)
                
                # Save compression statistics if requested
                if hasattr(flow_self, '_gradient_cache_stats'):
                    self._save_statistics(flow_self)
                    
                return result
                
            finally:
                # Clean up hooks
                if gradient_cache_state and 'hook_manager' in gradient_cache_state:
                    gradient_cache_state['hook_manager'].remove_hooks()
                    
        return wrapper
    
    def _initialize_gradient_cache(self, flow_self) -> Optional[dict]:
        """
        Set up the gradient cache system for a training step.
        
        Returns:
            Dictionary with gradient cache components, or None if failed
        """
        # Find the model in the flow
        model = self._find_model(flow_self)
        if model is None:
            warnings.warn("No PyTorch model found. Gradient cache disabled.")
            return None
            
        # Find the optimizer
        optimizer = self._find_optimizer(flow_self)
        if optimizer is None:
            warnings.warn("No optimizer found. Gradient cache disabled.")
            return None
        
        # Calculate sparsity from compression ratio
        sparsity = 1.0 - (1.0 / self.compression_ratio)
        
        # Parse memory budget
        if isinstance(self.memory_budget, str) and self.memory_budget.endswith('%'):
            memory_ratio = float(self.memory_budget.rstrip('%')) / 100
        else:
            memory_ratio = float(self.memory_budget)
        
        # Create core components
        compressor = AdaptiveGradientCompressor(
            initial_sparsity=sparsity,
            warmup_steps=self.warmup_steps,
            momentum_factor=0.9,
            gradient_clipping=1.0
        )
        
        memory_manager = GPUMemoryManager(
            memory_budget_ratio=memory_ratio,
            async_transfer=self.async_offload
        )
        
        hook_manager = GradientCacheHookManager(
            model=model,
            compressor=compressor,
            memory_manager=memory_manager,
            exclude_layers=self.exclude_layers,
            verbose=self.verbose
        )
        
        # Register hooks
        hook_manager.register_hooks()
        
        # Wrap the optimizer
        wrapped_optimizer = GradientCacheOptimizer(optimizer, hook_manager)
        
        # Replace the original optimizer
        # We need to find and replace it in flow_self
        for attr_name in dir(flow_self):
            attr = getattr(flow_self, attr_name)
            if attr is optimizer:
                setattr(flow_self, attr_name, wrapped_optimizer)
                break
        
        # Store state for cleanup and statistics
        gradient_cache_state = {
            'compressor': compressor,
            'memory_manager': memory_manager,
            'hook_manager': hook_manager,
            'wrapped_optimizer': wrapped_optimizer,
            'original_optimizer': optimizer
        }
        
        # Attach to flow for access in training loop
        flow_self._gradient_cache = gradient_cache_state
        flow_self._gradient_cache_stats = []
        
        if self.verbose:
            print(f"Gradient Cache initialized:")
            print(f"  - Compression ratio: {self.compression_ratio}x")
            print(f"  - Memory budget: {self.memory_budget}")
            print(f"  - Warmup steps: {self.warmup_steps}")
            print(f"  - Async offload: {self.async_offload}")
            
        return gradient_cache_state
    
    def _find_model(self, flow_self) -> Optional[nn.Module]:
        """
        Find a PyTorch model in the flow instance.
        
        Looks for common attribute names like 'model', 'net', etc.
        """
        # Common model attribute names
        model_names = ['model', 'net', 'network', 'module', 'backbone']
        
        for name in model_names:
            if hasattr(flow_self, name):
                attr = getattr(flow_self, name)
                if isinstance(attr, nn.Module):
                    return attr
                    
        # Search all attributes
        for attr_name in dir(flow_self):
            if not attr_name.startswith('_'):
                attr = getattr(flow_self, attr_name)
                if isinstance(attr, nn.Module):
                    return attr
                    
        return None
    
    def _find_optimizer(self, flow_self) -> Optional[torch.optim.Optimizer]:
        """
        Find a PyTorch optimizer in the flow instance.
        """
        # Common optimizer attribute names
        optimizer_names = ['optimizer', 'opt', 'optim']
        
        for name in optimizer_names:
            if hasattr(flow_self, name):
                attr = getattr(flow_self, name)
                if isinstance(attr, torch.optim.Optimizer):
                    return attr
                    
        # Search all attributes
        for attr_name in dir(flow_self):
            if not attr_name.startswith('_'):
                attr = getattr(flow_self, attr_name)
                if isinstance(attr, torch.optim.Optimizer):
                    return attr
                    
        return None
    
    def _save_statistics(self, flow_self) -> None:
        """
        Save compression statistics for analysis.
        """
        if not hasattr(flow_self, '_gradient_cache'):
            return
            
        hook_manager = flow_self._gradient_cache['hook_manager']
        memory_manager = flow_self._gradient_cache['memory_manager']
        
        # Get current statistics
        compression_summary = hook_manager.get_compression_summary()
        memory_stats = memory_manager.get_memory_stats()
        
        # Combine statistics
        stats = {
            'step': len(flow_self._gradient_cache_stats),
            'compression': compression_summary,
            'memory': {
                'gpu_allocated_gb': memory_stats.gpu_allocated_gb,
                'gpu_saved_gb': compression_summary.get('gpu_memory_saved_gb', 0),
                'cpu_buffer_gb': memory_stats.cpu_buffer_size_gb
            }
        }
        
        flow_self._gradient_cache_stats.append(stats)
        
        # Print summary every checkpoint_frequency steps
        if len(flow_self._gradient_cache_stats) % self.checkpoint_frequency == 0:
            print(f"\n=== Gradient Cache Statistics (Step {stats['step']}) ===")
            print(f"Overall compression ratio: {compression_summary['overall_compression_ratio']:.1f}x")
            print(f"GPU memory saved: {stats['memory']['gpu_saved_gb']:.2f} GB")
            print(f"CPU buffer size: {stats['memory']['cpu_buffer_gb']:.2f} GB")


# Create the main decorator function
optimize = GradientCacheDecorator