"""
Gradient scaler for automatic mixed precision training

This module provides the GradScaler class that handles gradient scaling
to prevent underflow when training with FP16 gradients.
"""

from typing import Any, Dict
from neurograd import xp
import numpy as real_np


class GradScaler:
    """
    Gradient scaler for automatic mixed precision training.
    """
    
    def __init__(self, 
                 init_scale: float = 128.0,
                 growth_factor: float = 2.0,
                 backoff_factor: float = 0.5,
                 growth_interval: int = 5000,
                 max_scale: float = 2**20,  # Add maximum scale limit
                 min_scale: float = 1.0,     # Add minimum scale limit
                 enabled: bool = True):
        """
        Initialize gradient scaler.
        
        Args:
            init_scale: Initial scaling factor
            growth_factor: Factor by which to multiply the scale when no overflow is detected
            backoff_factor: Factor by which to multiply the scale when overflow is detected  
            growth_interval: Number of steps between scale increases
            max_scale: Maximum allowed scale value (prevents unbounded growth)
            min_scale: Minimum allowed scale value
            enabled: Whether gradient scaling is enabled
        """
        if not enabled:
            self._enabled = False
            return
            
        self._enabled = True
        self._scale = float(init_scale)
        self._growth_factor = float(growth_factor)
        self._backoff_factor = float(backoff_factor)
        self._growth_interval = int(growth_interval)
        self._max_scale = float(max_scale)
        self._min_scale = float(min_scale)
        
        # Tracking variables
        self._growth_tracker = 0
        self._found_inf = False
        self._has_been_unscaled = False  # Track if unscale_ was called
        
    def unscale_(self, optimizer) -> None:
        """
        Unscale gradients in-place for the given optimizer.
        """
        if not self._enabled:
            return
        
        # Prevent double unscaling
        if self._has_been_unscaled:
            return
            
        # First, unscale all gradients
        inv_scale = 1.0 / self._scale if self._scale > 0 else 0.0
        found_inf = False
        
        for param_name, param in optimizer.params:
            if param.requires_grad and param.grad is not None:
                # Unscale gradient first
                param.grad = param.grad * inv_scale
                
                # Then check the UNSCALED gradient for inf/nan
                grad_data = param.grad
                if hasattr(grad_data, 'get'):  # CuPy array
                    grad_cpu = grad_data.get()
                else:
                    grad_cpu = grad_data
                
                if not real_np.isfinite(grad_cpu).all():
                    found_inf = True
                    # Zero out inf/nan gradients to prevent optimizer issues
                    param.grad = param.grad * 0
        
        self._found_inf = found_inf
        self._has_been_unscaled = True
    
    def step(self, optimizer) -> None:
        """
        Perform optimizer step with gradient scaling.
        """
        if not self._enabled:
            optimizer.step()
            return
        
        # Unscale gradients if not already done
        if not self._has_been_unscaled:
            self.unscale_(optimizer)
        
        # Only step if no overflow detected
        if not self._found_inf:
            optimizer.step()
    
    def update(self) -> None:
        """
        Update the scale factor based on recent gradient overflow status.
        """
        if not self._enabled:
            return
        
        if self._found_inf:
            # Overflow detected - reduce scale
            self._scale *= self._backoff_factor
            self._scale = max(self._scale, self._min_scale)
            self._growth_tracker = 0
        else:
            # No overflow - consider growing scale
            self._growth_tracker += 1
            if self._growth_tracker >= self._growth_interval:
                self._scale *= self._growth_factor
                # Clamp to maximum scale to prevent unbounded growth
                self._scale = min(self._scale, self._max_scale)
                self._growth_tracker = 0
        
        # Reset flags for next iteration
        self._found_inf = False
        self._has_been_unscaled = False
    
    def state_dict(self) -> Dict[str, Any]:
        """Get state dictionary for checkpointing."""
        return {
            'scale': self._scale,
            'growth_tracker': self._growth_tracker,
            'found_inf': self._found_inf,
            'growth_factor': self._growth_factor,
            'backoff_factor': self._backoff_factor,
            'growth_interval': self._growth_interval,
            'enabled': self._enabled
        }
    
    def load_state_dict(self, state_dict: Dict[str, Any]) -> None:
        """Load state dictionary from checkpoint."""
        self._scale = state_dict['scale']
        self._growth_tracker = state_dict['growth_tracker'] 
        self._found_inf = state_dict['found_inf']
        self._growth_factor = state_dict['growth_factor']
        self._backoff_factor = state_dict['backoff_factor']
        self._growth_interval = state_dict['growth_interval']
        self._enabled = state_dict['enabled']