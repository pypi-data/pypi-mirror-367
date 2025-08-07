"""
Adaptive Gradient Compressor with Momentum Correction

This implements the full Deep Gradient Compression (DGC) algorithm with:
1. Momentum correction to prevent gradient staleness
2. Adaptive layer-wise compression based on gradient statistics
3. Warm-up period for stable training start
4. Local gradient clipping for stability
"""

import torch
import torch.nn as nn
from typing import Dict, Optional, Tuple, List
import numpy as np
from collections import deque


class AdaptiveGradientCompressor:
    """
    Advanced gradient compressor that adapts compression ratios per layer
    and uses momentum to correct for compression errors.
    """
    
    def __init__(self, 
                 initial_sparsity: float = 0.99,
                 momentum_factor: float = 0.9,
                 gradient_clipping: float = 1.0,
                 warmup_steps: int = 1000,
                 window_size: int = 20):
        """
        Initialize the adaptive compressor.
        
        Args:
            initial_sparsity: Starting sparsity level (0.99 = keep 1%)
            momentum_factor: Exponential moving average factor for momentum
            gradient_clipping: Maximum gradient norm (prevents instability)
            warmup_steps: Steps before enabling full compression
            window_size: Number of steps to track for statistics
        """
        self.sparsity = initial_sparsity
        self.momentum_factor = momentum_factor
        self.gradient_clipping = gradient_clipping
        self.warmup_steps = warmup_steps
        self.window_size = window_size
        self.step = 0
        
        # Storage for momentum and error accumulation per layer
        self.momentum = {}
        self.error_accumulation = {}
        
        # Track statistics for adaptive compression
        self.layer_statistics = {}
        
    def compress(self, name: str, grad: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, Dict]:
        """
        Compress gradient with momentum correction and adaptive sparsity.
        
        The key innovations here:
        1. We accumulate compression errors to prevent information loss
        2. We adapt sparsity based on each layer's gradient patterns
        3. We use momentum to smooth out noisy gradients
        
        Args:
            name: Layer name (for tracking statistics)
            grad: The gradient tensor
            
        Returns:
            values: Compressed gradient values
            indices: Indices of kept values
            metadata: Compression statistics
        """
        self.step += 1
        
        # Initialize storage for this layer if needed
        if name not in self.momentum:
            self.momentum[name] = torch.zeros_like(grad)
            self.error_accumulation[name] = torch.zeros_like(grad)
            self.layer_statistics[name] = {
                'variance_history': deque(maxlen=self.window_size),
                'sparsity_history': deque(maxlen=self.window_size),
                'magnitude_history': deque(maxlen=self.window_size),
                'compression_ratios': deque(maxlen=self.window_size)
            }
        
        # Step 1: Apply local gradient clipping
        # This prevents any single gradient from dominating
        grad_norm = torch.norm(grad)
        if grad_norm > self.gradient_clipping:
            grad = grad * self.gradient_clipping / grad_norm
        
        # Step 2: Update momentum (exponential moving average)
        # This smooths out noisy gradients over time
        self.momentum[name] = (self.momentum_factor * self.momentum[name] + 
                              (1 - self.momentum_factor) * grad)
        
        # Step 3: Add accumulated error from previous compressions
        # This ensures no information is permanently lost
        corrected_grad = self.momentum[name] + self.error_accumulation[name]
        
        # Step 4: Determine adaptive sparsity for this layer
        sparsity = self._compute_adaptive_sparsity(name, corrected_grad)
        
        # Step 5: Compress using top-k selection
        k = max(1, int(corrected_grad.numel() * (1 - sparsity)))
        
        # Flatten for compression
        flat_grad = corrected_grad.view(-1)
        
        # Select top-k by absolute value
        topk_vals, topk_indices = torch.topk(flat_grad.abs(), k)
        threshold = topk_vals[-1]
        
        # Create mask for values above threshold
        mask = flat_grad.abs() >= threshold
        compressed_values = flat_grad[mask]
        compressed_indices = mask.nonzero(as_tuple=True)[0]
        
        # Step 6: Accumulate error (values we didn't send)
        sparse_grad = torch.zeros_like(flat_grad)
        sparse_grad[compressed_indices] = compressed_values
        self.error_accumulation[name] = (corrected_grad.view(-1) - sparse_grad).view(grad.shape)
        
        # Track statistics
        stats = self._update_statistics(name, grad, corrected_grad, sparsity, k)
        
        return compressed_values, compressed_indices, stats
    
    def _compute_adaptive_sparsity(self, name: str, grad: torch.Tensor) -> float:
        """
        Compute layer-specific sparsity based on gradient characteristics.
        
        The intuition: layers with stable, low-variance gradients can be
        compressed more aggressively without hurting training.
        """
        # During warmup, use less aggressive compression
        if self.step < self.warmup_steps:
            warmup_progress = self.step / self.warmup_steps
            # Gradually increase sparsity from 0.9 to target
            return 0.9 + (self.sparsity - 0.9) * warmup_progress
        
        stats = self.layer_statistics[name]
        
        # Compute current gradient statistics
        variance = grad.var().item()
        magnitude = grad.abs().mean().item()
        natural_sparsity = (grad.abs() < 1e-8).float().mean().item()
        
        # Add to history
        stats['variance_history'].append(variance)
        stats['magnitude_history'].append(magnitude)
        stats['sparsity_history'].append(natural_sparsity)
        
        # Need enough history to make decisions
        if len(stats['variance_history']) < 5:
            return self.sparsity
        
        # Compute rolling statistics
        avg_variance = np.mean(stats['variance_history'])
        variance_stability = np.std(stats['variance_history']) / (avg_variance + 1e-8)
        avg_magnitude = np.mean(stats['magnitude_history'])
        avg_natural_sparsity = np.mean(stats['sparsity_history'])
        
        # Adaptive rules based on layer characteristics
        adaptive_sparsity = self.sparsity
        
        # Rule 1: Layers with very low variance can be compressed more
        if avg_variance < 1e-6:
            adaptive_sparsity = min(0.999, self.sparsity + 0.05)
            
        # Rule 2: Layers with high natural sparsity can be compressed more
        elif avg_natural_sparsity > 0.5:
            adaptive_sparsity = min(0.999, self.sparsity + 0.02)
            
        # Rule 3: Critical layers (detected by name patterns) need less compression
        elif any(critical in name.lower() for critical in ['attention', 'embed', 'head']):
            adaptive_sparsity = max(0.9, self.sparsity - 0.05)
            
        # Rule 4: Unstable layers (high variance in variance) need less compression
        elif variance_stability > 0.5:
            adaptive_sparsity = max(0.9, self.sparsity - 0.03)
        
        return adaptive_sparsity
    
    def _update_statistics(self, name: str, original_grad: torch.Tensor, 
                          corrected_grad: torch.Tensor, sparsity: float, k: int) -> Dict:
        """Update and return compression statistics for monitoring."""
        stats = self.layer_statistics[name]
        
        compression_ratio = original_grad.numel() / k
        stats['compression_ratios'].append(compression_ratio)
        
        return {
            'layer': name,
            'step': self.step,
            'sparsity': sparsity,
            'compression_ratio': compression_ratio,
            'gradient_norm': original_grad.norm().item(),
            'corrected_norm': corrected_grad.norm().item(),
            'kept_values': k,
            'total_values': original_grad.numel(),
            'avg_compression_ratio': np.mean(stats['compression_ratios']) if stats['compression_ratios'] else compression_ratio
        }