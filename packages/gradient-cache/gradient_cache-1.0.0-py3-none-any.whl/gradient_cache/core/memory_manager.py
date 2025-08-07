"""
GPU Memory Manager

This module handles the critical task of moving compressed gradients between
GPU and CPU memory. The key insight: we can store compressed gradients on
CPU RAM (which is plentiful) and free up precious GPU memory for activations.
"""

import torch
from typing import Dict, Optional, Tuple, Any
import asyncio
from dataclasses import dataclass
import time


@dataclass
class MemoryStats:
    """Container for memory usage statistics"""
    gpu_allocated_gb: float
    gpu_reserved_gb: float
    gpu_max_allocated_gb: float
    cpu_buffer_size_gb: float
    compression_ratios: Dict[str, float]
    transfer_times: Dict[str, float]


class GPUMemoryManager:
    """
    Manages gradient storage and GPU-CPU transfers.
    
    The workflow:
    1. Receive compressed gradients from the compressor
    2. Asynchronously transfer them to CPU memory
    3. Free the GPU memory immediately
    4. Retrieve from CPU when optimizer needs them
    """
    
    def __init__(self, 
                 memory_budget_ratio: float = 0.8,
                 async_transfer: bool = True,
                 prefetch_ahead: int = 2):
        """
        Initialize memory manager.
        
        Args:
            memory_budget_ratio: Target GPU memory usage (0.8 = 80%)
            async_transfer: Use async CPU transfers (faster but complex)
            prefetch_ahead: Number of gradients to prefetch from CPU
        """
        self.memory_budget_ratio = memory_budget_ratio
        self.async_transfer = async_transfer
        self.prefetch_ahead = prefetch_ahead
        
        # CPU storage for compressed gradients
        self.cpu_buffer = {}
        
        # Original shapes for reconstruction
        self.shapes = {}
        
        # Track compression effectiveness
        self.compression_ratios = {}
        self.transfer_times = {}
        
        # Async transfer queue
        self.transfer_queue = []
        self.transfer_events = {}
        
        # Initialize CUDA streams for async transfers
        if torch.cuda.is_available() and async_transfer:
            self.transfer_stream = torch.cuda.Stream()
        else:
            self.transfer_stream = None
            
    def offload_gradient(self, name: str, 
                        compressed_values: torch.Tensor,
                        compressed_indices: torch.Tensor,
                        original_shape: torch.Size) -> None:
        """
        Offload compressed gradient to CPU memory.
        
        This is where the magic happens - we move the gradient off GPU
        to make room for more activations during forward pass.
        
        Args:
            name: Layer name
            compressed_values: The compressed gradient values
            compressed_indices: Indices for reconstruction
            original_shape: Shape of original gradient
        """
        start_time = time.time()
        
        # Store shape for later reconstruction
        self.shapes[name] = original_shape
        
        # Calculate compression ratio for monitoring
        original_size = torch.prod(torch.tensor(original_shape)) * 4  # 4 bytes per float32
        compressed_size = (len(compressed_values) + len(compressed_indices)) * 4
        self.compression_ratios[name] = compressed_size / original_size
        
        if self.async_transfer and self.transfer_stream is not None:
            # Asynchronous transfer using CUDA streams
            # This allows computation to continue while transfer happens
            with torch.cuda.stream(self.transfer_stream):
                # Create CPU tensors in pinned memory for faster transfer
                cpu_values = compressed_values.cpu()
                cpu_indices = compressed_indices.cpu()
                
                # Record event for synchronization
                event = torch.cuda.Event()
                event.record()
                self.transfer_events[name] = event
                
                # Store in CPU buffer
                self.cpu_buffer[name] = {
                    'values': cpu_values,
                    'indices': cpu_indices,
                    'dtype': compressed_values.dtype,
                    'device': compressed_values.device
                }
        else:
            # Synchronous transfer (simpler but blocks computation)
            self.cpu_buffer[name] = {
                'values': compressed_values.cpu(),
                'indices': compressed_indices.cpu(),
                'dtype': compressed_values.dtype,
                'device': compressed_values.device
            }
        
        # Track transfer time
        self.transfer_times[name] = time.time() - start_time
        
    def retrieve_gradient(self, name: str) -> torch.Tensor:
        """
        Retrieve gradient from CPU and reconstruct on GPU.
        
        Called when the optimizer needs the gradient for updates.
        
        Args:
            name: Layer name
            
        Returns:
            Reconstructed gradient tensor on GPU
        """
        if name not in self.cpu_buffer:
            raise KeyError(f"Gradient '{name}' not found in CPU buffer")
        
        # Wait for async transfer to complete if necessary
        if name in self.transfer_events:
            self.transfer_events[name].synchronize()
            del self.transfer_events[name]
        
        # Get compressed data
        data = self.cpu_buffer[name]
        original_shape = self.shapes[name]
        
        # Move back to GPU
        values = data['values'].to(data['device'])
        indices = data['indices'].to(data['device'])
        
        # Reconstruct full gradient
        total_elements = torch.prod(torch.tensor(original_shape))
        reconstructed = torch.zeros(total_elements, 
                                   dtype=data['dtype'], 
                                   device=data['device'])
        reconstructed[indices] = values
        
        # Reshape to original shape
        return reconstructed.view(original_shape)
    
    def get_memory_stats(self) -> MemoryStats:
        """
        Get comprehensive memory usage statistics.
        
        This helps monitor the effectiveness of gradient caching.
        """
        stats = MemoryStats(
            gpu_allocated_gb=0,
            gpu_reserved_gb=0,
            gpu_max_allocated_gb=0,
            cpu_buffer_size_gb=0,
            compression_ratios=self.compression_ratios.copy(),
            transfer_times=self.transfer_times.copy()
        )
        
        if torch.cuda.is_available():
            # GPU memory stats
            stats.gpu_allocated_gb = torch.cuda.memory_allocated() / 1024**3
            stats.gpu_reserved_gb = torch.cuda.memory_reserved() / 1024**3
            stats.gpu_max_allocated_gb = torch.cuda.max_memory_allocated() / 1024**3
        
        # CPU buffer size
        cpu_size = 0
        for data in self.cpu_buffer.values():
            cpu_size += data['values'].element_size() * data['values'].nelement()
            cpu_size += data['indices'].element_size() * data['indices'].nelement()
        stats.cpu_buffer_size_gb = cpu_size / 1024**3
        
        return stats
    
    def should_increase_compression(self) -> bool:
        """
        Determine if we should increase compression based on memory pressure.
        
        This enables adaptive memory management - compress more when running low.
        """
        if not torch.cuda.is_available():
            return False
            
        current_usage = torch.cuda.memory_allocated() / torch.cuda.get_device_properties(0).total_memory
        return current_usage > self.memory_budget_ratio
    
    def clear_buffers(self):
        """Clear all CPU buffers to free memory."""
        self.cpu_buffer.clear()
        self.shapes.clear()
        self.compression_ratios.clear()
        self.transfer_times.clear()
        self.transfer_events.clear()
        
    def __del__(self):
        """Cleanup on deletion."""
        self.clear_buffers()