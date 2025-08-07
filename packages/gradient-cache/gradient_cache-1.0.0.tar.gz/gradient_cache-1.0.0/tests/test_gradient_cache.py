"""
Gradient Cache Test Suite

Basic tests to ensure the package is working correctly.
"""

import pytest
import torch
import torch.nn as nn
import gradient_cache


def test_compression():
    """Test basic gradient compression."""
    compressor = gradient_cache.GradientCompressor(sparsity=0.99)
    
    # Create test gradient
    grad = torch.randn(1000, 1000)
    values, indices = compressor.compress(grad)
    
    # Check compression ratio
    assert len(values) == 10000  # 1% of 1M
    assert len(indices) == 10000
    
    # Check decompression
    decompressed = compressor.decompress(values, indices, grad.shape)
    assert decompressed.shape == grad.shape


def test_gradient_cache_integration():
    """Test full gradient cache system."""
    # Create simple model
    model = nn.Linear(100, 100)
    if torch.cuda.is_available():
        model = model.cuda()
    
    # Setup gradient cache
    hook_manager = gradient_cache.create_gradient_cache(
        model,
        compression_ratio=10,
        verbose=False
    )
    
    # Run forward/backward
    x = torch.randn(32, 100)
    if torch.cuda.is_available():
        x = x.cuda()
    
    y = model(x).mean()
    y.backward()
    
    # Compress gradients
    hook_manager.compress_and_free_gradients()
    
    # Verify gradients are freed
    assert all(p.grad is None for p in model.parameters())
    
    # Restore and verify
    hook_manager.apply_gradients()
    assert all(p.grad is not None for p in model.parameters())


def test_memory_savings():
    """Test that memory is actually saved."""
    if not torch.cuda.is_available():
        pytest.skip("GPU required for memory test")
    
    model = nn.Sequential(
        nn.Linear(1000, 1000),
        nn.ReLU(),
        nn.Linear(1000, 1000)
    ).cuda()
    
    # Baseline
    x = torch.randn(32, 1000).cuda()
    y = model(x).mean()
    
    torch.cuda.synchronize()
    before = torch.cuda.memory_allocated()
    
    y.backward()
    
    torch.cuda.synchronize()
    after_backward = torch.cuda.memory_allocated()
    
    # With compression
    model.zero_grad()
    hook_manager = gradient_cache.create_gradient_cache(model)
    
    y = model(x).mean()
    y.backward()
    hook_manager.compress_and_free_gradients()
    
    torch.cuda.synchronize()
    after_compression = torch.cuda.memory_allocated()
    
    # Should save significant memory
    baseline_grad_memory = after_backward - before
    compressed_memory = after_compression - before
    
    assert compressed_memory < baseline_grad_memory * 0.2  # At least 80% savings


if __name__ == "__main__":
    test_compression()
    print("✓ Compression test passed")
    
    test_gradient_cache_integration()
    print("✓ Integration test passed")
    
    if torch.cuda.is_available():
        test_memory_savings()
        print("✓ Memory savings test passed")
    
    print("\nAll tests passed!")
