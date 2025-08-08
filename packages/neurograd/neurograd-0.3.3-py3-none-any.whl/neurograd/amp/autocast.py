"""
Simplified autocast context manager for automatic mixed precision.

This module provides a PyTorch-like autocast context manager that automatically
selects appropriate precision for tensor operations.
"""

import threading
from typing import Optional, Dict, Any
from neurograd import xp


# Global autocast state - using module-level variables instead of thread-local
# for better performance and simpler integration
_autocast_state = {
    'enabled': False,
    'device_type': 'cuda',
    'dtype': xp.float32,
    'cache_enabled': True
}


class autocast:
    """
    Context manager that enables automatic mixed precision.
    
    PyTorch-like implementation that automatically casts operations to lower
    precision (typically FP16) for speed while maintaining numerical stability.
    
    Example:
        >>> with autocast(device_type="cuda", dtype=xp.float16):
        ...     output = model(input)
        ...     loss = loss_fn(target, output)
    """
    
    def __init__(self, 
                 device_type: str = "cuda", 
                 enabled: bool = True,
                 dtype: Optional[Any] = None,
                 cache_enabled: bool = True):
        """
        Initialize autocast context manager.
        
        Args:
            device_type: Device type ("cuda" or "cpu"). Only CUDA benefits from mixed precision.
            enabled: Whether autocast is enabled. If False, operations run in their original precision.
            dtype: Target dtype for autocasting. Defaults to float16 for CUDA, float32 for CPU.
            cache_enabled: Whether to cache autocast-compatible kernels (currently unused but kept for API compatibility).
        """
        if device_type not in ("cuda", "cpu"):
            raise ValueError(f"Unsupported device type: {device_type}. Must be 'cuda' or 'cpu'")
        
        self.device_type = device_type
        # Enable for both CPU and CUDA - let user control via enabled parameter
        self.enabled = enabled
        self.cache_enabled = cache_enabled
        
        # Determine target dtype
        if dtype is None:
            self.dtype = xp.float16 if self.enabled else xp.float32
        else:
            if isinstance(dtype, str):
                if hasattr(xp, dtype):
                    self.dtype = getattr(xp, dtype)
                else:
                    raise ValueError(f"Unknown dtype: {dtype}")
            else:
                self.dtype = dtype
        
        # Store previous state for restoration
        self._prev_state = None

    def __enter__(self):
        """Enter the autocast context."""
        global _autocast_state
        
        # Save current state
        self._prev_state = _autocast_state.copy()
        
        # Set new state
        _autocast_state['enabled'] = self.enabled
        _autocast_state['device_type'] = self.device_type
        _autocast_state['dtype'] = self.dtype
        _autocast_state['cache_enabled'] = self.cache_enabled
        
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the autocast context."""
        global _autocast_state
        
        # Restore previous state
        if self._prev_state is not None:
            _autocast_state.update(self._prev_state)
        else:
            # Fallback to defaults if no previous state
            _autocast_state['enabled'] = False
            _autocast_state['device_type'] = 'cuda'
            _autocast_state['dtype'] = xp.float32
            _autocast_state['cache_enabled'] = True

    @staticmethod
    def is_enabled() -> bool:
        """Check if autocast is currently enabled."""
        return _autocast_state['enabled']
    
    @staticmethod
    def get_autocast_dtype():
        """Get the current autocast dtype."""
        return _autocast_state['dtype']
    
    @staticmethod
    def get_autocast_device() -> str:
        """Get the current autocast device type."""
        return _autocast_state['device_type']
    
    @staticmethod
    def is_autocast_cache_enabled() -> bool:
        """Check if autocast caching is enabled."""
        return _autocast_state['cache_enabled']


# Operation categorization - simplified and more targeted
_FP32_OPS = frozenset([
    # Loss functions - need high precision for numerical stability
    'cross_entropy', 'mse_loss', 'l1_loss', 'smooth_l1_loss', 'binary_cross_entropy',
    'categoricalcrossentropy', 'mse',
    
    # Normalization operations - sensitive to precision
    'layer_norm', 'batch_norm', 'softmax', 'log_softmax',
    
    # Mathematical operations that can underflow/overflow in FP16
    'exp', 'log', 'sqrt', 'pow',
    
    # Reduction operations - can accumulate errors
    'sum', 'mean', 'std', 'var', 'norm',
    
    # Casting operations
    'cast'
])

_FP16_SAFE_OPS = frozenset([
    # Linear algebra - benefits most from FP16 Tensor Cores
    'matmul', 'linear', 'conv2d',
    
    # Element-wise operations - generally safe
    'add', 'sub', 'mul', 'div',
    
    # Activations - mostly safe except some edge cases
    'relu', 'gelu', 'tanh', 'sigmoid',
    
    # Shape operations - safe
    'transpose', 'reshape', 'flatten',
    
    # Pooling operations
    'max', 'min', 'maxpool2d', 'averagepool2d'
])


def should_autocast(op_name: str) -> bool:
    """
    Determine if an operation should be autocasted to lower precision.
    
    Args:
        op_name: Name of the operation
        
    Returns:
        True if operation should use autocast dtype, False to keep original precision
    """
    if not is_autocast_enabled():
        return False
    
    if not op_name:
        return True  # Default to casting for unknown ops
    
    op_name_lower = op_name.lower()
    
    # Explicitly keep these in FP32 for numerical stability
    if op_name_lower in _FP32_OPS:
        return False
        
    # Everything else gets cast for speed
    return True


def autocast_tensor(tensor, op_name: str = ""):
    """
    Cast tensor to autocast dtype if appropriate.
    
    Args:
        tensor: Input tensor
        op_name: Name of the operation (for deciding whether to cast)
        
    Returns:
        Tensor cast to appropriate dtype
    """
    from neurograd.tensor import Tensor
    
    if not isinstance(tensor, Tensor) or not should_autocast(op_name):
        return tensor
    
    target_dtype = get_autocast_dtype()
    
    # Fast path: skip if already correct dtype
    if tensor.data.dtype == target_dtype:
        return tensor
        
    return tensor.cast(target_dtype)


# Convenience functions for backward compatibility and ease of use
def is_autocast_enabled() -> bool:
    """Check if autocast is currently enabled (convenience function).""" 
    return autocast.is_enabled()


def get_autocast_dtype():
    """Get current autocast dtype (convenience function)."""
    return autocast.get_autocast_dtype()


def get_autocast_device() -> str:
    """Get current autocast device type (convenience function)."""
    return autocast.get_autocast_device()


def is_autocast_cache_enabled() -> bool:
    """Check if autocast caching is enabled (convenience function)."""
    return autocast.is_autocast_cache_enabled()


def set_autocast_enabled(enabled: bool) -> None:
    """Enable or disable autocast globally (for debugging)."""
    global _autocast_state
    _autocast_state['enabled'] = enabled


def set_autocast_dtype(dtype) -> None:
    """Set autocast dtype globally (for debugging)."""
    global _autocast_state
    _autocast_state['dtype'] = dtype