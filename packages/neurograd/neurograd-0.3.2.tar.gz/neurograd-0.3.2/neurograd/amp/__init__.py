"""
NeuroGrad Automatic Mixed Precision (AMP) Module

This module provides simplified PyTorch-like automatic mixed precision training capabilities,
enabling faster training and reduced memory usage while maintaining numerical stability.

The module is organized into two main components:
- autocast: Context manager for automatic precision casting
- GradScaler: Gradient scaling for FP16 training stability

Example usage:
    >>> from neurograd.amp import autocast, GradScaler
    >>> 
    >>> scaler = GradScaler()
    >>> for inputs, targets in dataloader:
    ...     optimizer.zero_grad()
    ...     with autocast(device_type="cuda", dtype=xp.float16):
    ...         outputs = model(inputs)
    ...         loss = loss_fn(outputs, targets)
    ...     
    ...     scaler.scale(loss).backward()
    ...     scaler.step(optimizer)
    ...     scaler.update()
"""

from .autocast import (
    autocast, 
    is_autocast_enabled, 
    get_autocast_dtype,
    get_autocast_device,
    is_autocast_cache_enabled,
    set_autocast_enabled,
    set_autocast_dtype,
    autocast_tensor,
    should_autocast
)
from .grad_scaler import GradScaler

# For backward compatibility and convenience
__all__ = [
    'autocast',
    'GradScaler',
    'is_autocast_enabled',
    'get_autocast_dtype', 
    'get_autocast_device',
    'is_autocast_cache_enabled',
    'set_autocast_enabled',
    'set_autocast_dtype',
    'autocast_tensor',
    'should_autocast'
]