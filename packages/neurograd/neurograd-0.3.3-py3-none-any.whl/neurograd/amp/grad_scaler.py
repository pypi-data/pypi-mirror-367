"""
Simplified gradient scaler for automatic mixed precision training.

This module provides a PyTorch-like GradScaler class that handles gradient scaling
to prevent underflow when training with FP16 gradients.
"""

from typing import Any, Dict, Optional, List, Tuple
from neurograd import xp
import numpy as real_np


class GradScaler:
    """
    Gradient scaler for automatic mixed precision training.
    
    Simplified PyTorch-like implementation that scales the loss to prevent
    gradient underflow in FP16 training, then unscales gradients before
    optimizer step.
    
    Example:
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
    
    def __init__(self, 
                 device: str = "cuda",
                 init_scale: float = 65536.0,  # 2^16
                 growth_factor: float = 2.0,
                 backoff_factor: float = 0.5,
                 growth_interval: int = 2000,
                 enabled: bool = True):
        """
        Initialize gradient scaler.
        
        Args:
            device: Device type ("cuda" or "cpu"). AMP only benefits CUDA.
            init_scale: Initial scaling factor
            growth_factor: Factor to multiply scale when no overflow detected
            backoff_factor: Factor to multiply scale when overflow detected  
            growth_interval: Number of successful steps between scale increases
            enabled: Whether gradient scaling is enabled
        """
        self._device = device
        # Enable for both CPU and CUDA for testing - user can disable if needed
        self._enabled = enabled
        
        if self._enabled:
            self._scale = float(init_scale)
            self._growth_factor = float(growth_factor)
            self._backoff_factor = float(backoff_factor) 
            self._growth_interval = int(growth_interval)
            self._growth_tracker = 0
            self._found_inf_per_device = {}  # Track per-device inf detection
        else:
            # Disabled - set dummy values
            self._scale = 1.0
            
    def is_enabled(self) -> bool:
        """Check if gradient scaling is enabled."""
        return self._enabled
    
    def get_scale(self) -> float:
        """Get current scale factor."""
        return self._scale if self._enabled else 1.0
    
    def scale(self, outputs):
        """
        Scale tensor(s) by the current scale factor.
        
        Args:
            outputs: Tensor or iterable of tensors to scale (usually loss)
            
        Returns:
            Scaled tensor(s) with same structure as input
        """
        if not self._enabled:
            return outputs
        
        from neurograd.tensor import Tensor
        
        def _scale_tensor(tensor):
            if not isinstance(tensor, Tensor):
                # Convert to tensor if needed
                if hasattr(tensor, '__array__') or isinstance(tensor, (int, float)):
                    tensor = Tensor(xp.array(tensor), requires_grad=False)
                else:
                    raise TypeError(f"Cannot scale object of type {type(tensor)}")
            
            # Scale by creating a new tensor with scaled data
            # This preserves the computational graph
            scale_data = xp.array(self._scale, dtype=tensor.data.dtype)
            from neurograd.functions.arithmetic import Mul
            mul_op = Mul()
            return mul_op(tensor, Tensor(scale_data, requires_grad=False))
        
        # Handle both single tensors and iterables
        if hasattr(outputs, '__iter__') and not isinstance(outputs, Tensor):
            return type(outputs)(_scale_tensor(output) for output in outputs)
        else:
            return _scale_tensor(outputs)
    
    def unscale_(self, optimizer) -> None:
        """
        Unscale gradients in-place for the given optimizer.
        
        Must be called before optimizer.step() to restore gradients to their
        original magnitude. Also detects gradient overflow.
        
        Args:
            optimizer: Optimizer whose parameters' gradients should be unscaled
        """
        if not self._enabled:
            return
        
        device_key = self._device
        found_inf = False
        
        # Check all parameters with gradients - optimized for speed
        for param_name, param in optimizer.params:
            if param.requires_grad and param.grad is not None:
                # Fast path: assume param.grad is already correct type
                # Only check for inf/nan on float/complex types
                if param.grad.dtype.kind in 'fc':
                    # Use any() for early termination - faster than all()
                    if not xp.all(xp.isfinite(param.grad)):
                        found_inf = True
                        break
                
                # Unscale gradient in-place - fast path
                if self._scale > 0:
                    param.grad = param.grad / self._scale
        
        # Store overflow status for this device
        self._found_inf_per_device[device_key] = found_inf
    
    def step(self, optimizer, *args, **kwargs) -> Optional[float]:
        """
        Perform optimizer step with gradient scaling.
        
        Unscales gradients, checks for overflow, and conditionally runs
        the optimizer step. Returns the scale value used.
        
        Args:
            optimizer: Optimizer to step
            *args, **kwargs: Additional arguments passed to optimizer.step()
            
        Returns:
            Scale factor used, or None if step was skipped due to overflow
        """
        if not self._enabled:
            optimizer.step(*args, **kwargs)
            return 1.0
        
        # Unscale gradients first
        self.unscale_(optimizer)
        
        # Check if any device found inf
        found_inf = any(self._found_inf_per_device.values())
        
        if not found_inf:
            # Safe to step
            optimizer.step(*args, **kwargs)
            return self._scale
        else:
            # Skip step due to overflow
            return None
    
    def update(self, new_scale: Optional[float] = None) -> None:
        """
        Update the scale factor based on recent gradient overflow status.
        
        Should be called after each training step to adjust the scale factor
        for the next iteration.
        
        Args:
            new_scale: If provided, sets the scale to this value instead of
                      using the automatic growth/backoff logic
        """
        if not self._enabled:
            return
        
        if new_scale is not None:
            self._scale = float(new_scale)
            self._growth_tracker = 0
            self._found_inf_per_device.clear()
            return
        
        # Check if any device found inf in the last step
        found_inf = any(self._found_inf_per_device.values())
        
        if found_inf:
            # Overflow detected - reduce scale
            self._scale *= self._backoff_factor
            self._scale = max(self._scale, 1.0)  # Minimum scale
            self._growth_tracker = 0
        else:
            # No overflow - consider growing scale
            self._growth_tracker += 1
            if self._growth_tracker >= self._growth_interval:
                self._scale *= self._growth_factor
                self._growth_tracker = 0
        
        # Clear overflow tracking for next step
        self._found_inf_per_device.clear()
    
    def get_backoff_factor(self) -> float:
        """Get the backoff factor used to reduce scale on overflow."""
        return self._backoff_factor if self._enabled else 1.0
    
    def get_growth_factor(self) -> float:
        """Get the growth factor used to increase scale."""
        return self._growth_factor if self._enabled else 1.0
        
    def get_growth_interval(self) -> int:
        """Get the interval between scale increases.""" 
        return self._growth_interval if self._enabled else 1
    
    def is_scale_updated(self) -> bool:
        """Check if scale was updated in the last update() call."""
        # Simple approximation - in practice you'd track this more precisely
        return len(self._found_inf_per_device) > 0 if self._enabled else False
    
    def state_dict(self) -> Dict[str, Any]:
        """Get state dictionary for checkpointing."""
        return {
            'scale': self._scale,
            'growth_tracker': getattr(self, '_growth_tracker', 0),
            'found_inf_per_device': getattr(self, '_found_inf_per_device', {}),
            'growth_factor': getattr(self, '_growth_factor', 2.0),
            'backoff_factor': getattr(self, '_backoff_factor', 0.5),
            'growth_interval': getattr(self, '_growth_interval', 2000),
            'enabled': self._enabled,
            'device': self._device
        }
    
    def load_state_dict(self, state_dict: Dict[str, Any]) -> None:
        """Load state dictionary from checkpoint."""
        self._scale = state_dict['scale']
        if self._enabled:
            self._growth_tracker = state_dict.get('growth_tracker', 0)
            self._found_inf_per_device = state_dict.get('found_inf_per_device', {})
            self._growth_factor = state_dict.get('growth_factor', 2.0)
            self._backoff_factor = state_dict.get('backoff_factor', 0.5)
            self._growth_interval = state_dict.get('growth_interval', 2000)
        
        self._enabled = state_dict.get('enabled', True)
        self._device = state_dict.get('device', 'cuda')
    
    def __repr__(self) -> str:
        return (f"GradScaler(device='{self._device}', enabled={self._enabled}, "
                f"scale={self.get_scale():.1f})")