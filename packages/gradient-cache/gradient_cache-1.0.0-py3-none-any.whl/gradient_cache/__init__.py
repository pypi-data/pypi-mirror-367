"""
Gradient Cache - GPU Memory-Efficient Training

A production-ready system that reduces GPU memory usage by 90%+ during
neural network training through intelligent gradient compression.

Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Gradient Cache Contributors"

# Import core components
from .core.compressor import GradientCompressor
from .core.adaptive_compressor import AdaptiveGradientCompressor
from .core.memory_manager import GPUMemoryManager, MemoryStats
from .core.hook_manager import GradientCacheHookManager

# Main user interface
from .integrations.metaflow_decorator import optimize, GradientCacheDecorator

# Convenience function
def create_gradient_cache(model, compression_ratio=100, verbose=False):
    """
    Quick helper to create a gradient cache for any model.
    
    Args:
        model: PyTorch model
        compression_ratio: How much to compress (100 = keep 1%)
        verbose: Print compression stats
        
    Returns:
        GradientCacheHookManager instance
    """
    return GradientCacheHookManager(
        model,
        compression_ratio=compression_ratio,
        verbose=verbose
    )

# Public API
__all__ = [
    # Main interface
    'optimize',
    'create_gradient_cache',
    'GradientCacheHookManager',
    
    # Core components
    'GradientCompressor',
    'AdaptiveGradientCompressor', 
    'GPUMemoryManager',
    'MemoryStats',
    
    # Version
    '__version__',
]
