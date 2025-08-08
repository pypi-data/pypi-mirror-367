"""
Gradient Scaler for Mixed Precision Training in NeuroGrad

Handles gradient scaling to prevent underflow when using FP16 gradients.
"""

import neurograd as ng
from neurograd import xp
from typing import Dict, List, Optional, Union
import math

class GradScaler:
    """
    Gradient scaler for automatic mixed precision training.
    
    Scales gradients to prevent underflow in FP16, then unscales before
    optimizer steps and detects overflow/underflow for dynamic scaling.
    """
    
    def __init__(self, 
                 init_scale: float = 2**16,
                 growth_factor: float = 2.0,
                 backoff_factor: float = 0.5,
                 growth_interval: int = 2000,
                 enabled: bool = True):
        """
        Initialize gradient scaler.
        
        Args:
            init_scale: Initial loss scale value
            growth_factor: Factor to multiply scale by when no overflow
            backoff_factor: Factor to multiply scale by when overflow detected
            growth_interval: Number of steps between scale increases
            enabled: Whether scaling is enabled
        """
        self._scale = float(init_scale)
        self._growth_factor = growth_factor
        self._backoff_factor = backoff_factor
        self._growth_interval = growth_interval
        self._growth_tracker = 0
        self._enabled = enabled
        
        # For overflow detection
        self._found_inf_per_device = {}
        
    def scale(self, outputs):
        """
        Scale loss or tensor outputs.
        
        Args:
            outputs: Tensor or list of tensors to scale
            
        Returns:
            Scaled tensor(s)
        """
        if not self._enabled:
            return outputs
            
        if isinstance(outputs, (list, tuple)):
            return [self._scale_tensor(output) for output in outputs]
        else:
            return self._scale_tensor(outputs)
    
    def _scale_tensor(self, tensor):
        """Scale a single tensor"""
        if not isinstance(tensor, ng.Tensor):
            raise TypeError(f"Expected Tensor, got {type(tensor)}")
        
        # Create scaled tensor
        scaled_data = tensor.data * self._scale
        scaled_tensor = ng.Tensor(
            scaled_data, 
            requires_grad=tensor.requires_grad,
            grad_fn=tensor.grad_fn,
            name=f"{tensor.name}_scaled"
        )
        return scaled_tensor
    
    def step(self, optimizer, *args, **kwargs):
        """
        Step the optimizer with gradient unscaling and overflow checking.
        
        Args:
            optimizer: Optimizer to step
            *args, **kwargs: Additional arguments for optimizer.step()
        """
        if not self._enabled:
            optimizer.step(*args, **kwargs)
            return
        
        # Unscale gradients
        self._unscale_grads(optimizer)
        
        # Check for overflow/underflow
        found_inf = self._check_overflow(optimizer)
        
        if not found_inf:
            # Safe to step optimizer
            optimizer.step(*args, **kwargs)
            self._growth_tracker += 1
        else:
            # Skip optimizer step due to overflow
            optimizer.zero_grad()
            
        # Update scale
        self.update()
    
    def unscale_(self, optimizer):
        """
        Manually unscale gradients (useful for gradient clipping).
        
        Args:
            optimizer: Optimizer whose gradients to unscale
        """
        if self._enabled:
            self._unscale_grads(optimizer)
    
    def _unscale_grads(self, optimizer):
        """Unscale all gradients in the optimizer"""
        inv_scale = 1.0 / self._scale
        
        for param_group in self._get_param_groups(optimizer):
            for param_item in param_group:
                # Handle NeuroGrad's (name, param) tuple format
                if isinstance(param_item, tuple):
                    name, param = param_item
                else:
                    param = param_item
                
                if param.grad is not None:
                    param.grad = param.grad * inv_scale
    
    def _get_param_groups(self, optimizer):
        """Get parameter groups from optimizer"""
        # NeuroGrad optimizers store params as a list of (name, param) tuples
        if hasattr(optimizer, 'params'):
            # Return params as a single group - params is already a list of (name, param) tuples
            return [optimizer.params]
        else:
            raise AttributeError(f"Unsupported optimizer type: {type(optimizer)}")
    
    def _check_overflow(self, optimizer) -> bool:
        """
        Check for gradient overflow/underflow.
        
        Returns:
            bool: True if overflow detected
        """
        found_inf = False
        
        for param_group in self._get_param_groups(optimizer):
            for param_item in param_group:
                # Handle NeuroGrad's (name, param) tuple format
                if isinstance(param_item, tuple):
                    name, param = param_item
                else:
                    param = param_item
                
                if param.grad is not None:
                    # Check for inf/nan in gradients
                    grad_data = param.grad
                    if hasattr(grad_data, 'get'):  # CuPy array
                        grad_data = grad_data.get()
                    
                    if not self._is_finite(grad_data):
                        found_inf = True
                        break
            
            if found_inf:
                break
        
        return found_inf
    
    def _is_finite(self, tensor_data):
        """Check if tensor contains only finite values"""
        import numpy as np
        return np.isfinite(tensor_data).all()
    
    def update(self, new_scale: Optional[float] = None):
        """
        Update the loss scale.
        
        Args:
            new_scale: Optional new scale value to set directly
        """
        if not self._enabled:
            return
            
        if new_scale is not None:
            self._scale = new_scale
            self._growth_tracker = 0
            return
        
        # Check if we found overflow in last step
        found_inf = len(self._found_inf_per_device) > 0
        self._found_inf_per_device.clear()
        
        if found_inf:
            # Overflow detected - decrease scale
            self._scale *= self._backoff_factor
            self._growth_tracker = 0
        else:
            # No overflow - potentially increase scale
            if self._growth_tracker >= self._growth_interval:
                self._scale *= self._growth_factor
                self._growth_tracker = 0
    
    def get_scale(self) -> float:
        """Get current loss scale value"""
        return self._scale
    
    def set_scale(self, new_scale: float):
        """Set loss scale value"""
        self._scale = float(new_scale)
        self._growth_tracker = 0
    
    def is_enabled(self) -> bool:
        """Check if scaling is enabled"""
        return self._enabled
    
    def state_dict(self) -> Dict:
        """Get state dictionary for checkpointing"""
        return {
            'scale': self._scale,
            'growth_factor': self._growth_factor,
            'backoff_factor': self._backoff_factor,
            'growth_interval': self._growth_interval,
            'growth_tracker': self._growth_tracker,
            'enabled': self._enabled
        }
    
    def load_state_dict(self, state_dict: Dict):
        """Load state dictionary from checkpoint"""
        self._scale = state_dict['scale']
        self._growth_factor = state_dict['growth_factor']
        self._backoff_factor = state_dict['backoff_factor']
        self._growth_interval = state_dict['growth_interval']
        self._growth_tracker = state_dict['growth_tracker']
        self._enabled = state_dict['enabled']
    
    def __repr__(self):
        return (f"GradScaler(scale={self._scale}, growth_factor={self._growth_factor}, "
                f"backoff_factor={self._backoff_factor}, enabled={self._enabled})")


class SimpleGradScaler:
    """
    Simplified gradient scaler for basic mixed precision training.
    
    Uses fixed scaling without dynamic adjustment.
    """
    
    def __init__(self, scale: float = 1024.0, enabled: bool = True):
        """
        Initialize simple gradient scaler.
        
        Args:
            scale: Fixed scale value
            enabled: Whether scaling is enabled
        """
        self._scale = float(scale)
        self._enabled = enabled
    
    def scale(self, loss):
        """Scale loss tensor"""
        if not self._enabled:
            return loss
        return loss * self._scale
    
    def step(self, optimizer, *args, **kwargs):
        """Step optimizer with gradient unscaling"""
        if self._enabled:
            # Unscale gradients
            inv_scale = 1.0 / self._scale
            for name, param in optimizer.params:
                if param.grad is not None:
                    param.grad = param.grad * inv_scale
        
        optimizer.step(*args, **kwargs)
    
    def get_scale(self) -> float:
        """Get current scale value"""
        return self._scale
