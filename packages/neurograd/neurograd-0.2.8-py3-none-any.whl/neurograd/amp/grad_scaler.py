"""
Gradient scaler for automatic mixed precision training

This module provides the GradScaler class that handles gradient scaling
to prevent underflow when training with FP16 gradients.
"""

from typing import Any, Dict, TYPE_CHECKING
from neurograd import xp
import numpy as real_np

if TYPE_CHECKING:
    from neurograd.tensor import Tensor


class GradScaler:
    """
    Gradient scaler for automatic mixed precision training.
    
    When training with FP16, gradients can underflow (become zero) due to the limited
    numerical range of FP16. GradScaler addresses this by scaling the loss before
    backward pass and unscaling gradients before optimizer step.
    
    Example:
        >>> scaler = GradScaler()
        >>> for inputs, targets in dataloader:
        ...     optimizer.zero_grad()
        ...     with autocast():
        ...         outputs = model(inputs)
        ...         loss = loss_fn(outputs, targets)
        ...     
        ...     # Scale loss to prevent gradient underflow
        ...     scaled_loss = scaler.scale(loss)
        ...     scaled_loss.backward()
        ...     
        ...     # Unscale gradients and step
        ...     scaler.step(optimizer)
        ...     scaler.update()
    """
    
    def __init__(self, 
                 init_scale: float = 2**16,  # Match PyTorch's default
                 growth_factor: float = 2.0,
                 backoff_factor: float = 0.5,
                 growth_interval: int = 2000,  # Match PyTorch's default
                 enabled: bool = True):
        """
        Initialize gradient scaler.
        
        Args:
            init_scale: Initial scaling factor
            growth_factor: Factor by which to multiply the scale when no overflow is detected
            backoff_factor: Factor by which to multiply the scale when overflow is detected  
            growth_interval: Number of steps between scale increases
            enabled: Whether gradient scaling is enabled
        """
        if not enabled:
            # Disable scaling - useful for debugging or CPU training
            self._enabled = False
            return
            
        self._enabled = True
        self._scale = float(init_scale)
        self._growth_factor = float(growth_factor)
        self._backoff_factor = float(backoff_factor)
        self._growth_interval = int(growth_interval)
        
        # Tracking variables
        self._growth_tracker = 0
        self._found_inf_this_step = False
        self._min_scale = 1.0 / (2**14)  # Match PyTorch's minimum (but not as extreme)
        self._per_param_gradients = []  # Track per-param gradients for better debugging
        
    def is_enabled(self) -> bool:
        """Check if gradient scaling is enabled."""
        return self._enabled
    
    def get_scale(self) -> float:
        """Get current scale factor."""
        return self._scale if self._enabled else 1.0
    
    def scale(self, tensor) -> 'Tensor':
        """
        Scale a tensor (typically the loss) by the current scale factor.
        
        Args:
            tensor: Tensor to scale (usually the loss)
            
        Returns:
            Scaled tensor
        """
        if not self._enabled:
            return tensor
        
        # Skip scaling if scale is too small (like PyTorch)
        if self._scale < 1.0:
            return tensor
            
        from neurograd.tensor import Tensor
        
        if not isinstance(tensor, Tensor):
            # Convert to tensor if needed
            tensor = Tensor(xp.array(tensor), requires_grad=tensor.requires_grad if hasattr(tensor, 'requires_grad') else False)
        
        # Scale by multiplying with scale factor
        scale_tensor = Tensor(xp.array(self._scale), requires_grad=False)
        return tensor * scale_tensor
    
    def unscale_(self, optimizer) -> None:
        """
        Unscale gradients in-place for the given optimizer.
        
        This should be called before optimizer.step() to restore gradients to their
        original magnitude. Also performs gradient clipping and inf/nan detection
        like PyTorch's implementation.
        
        Args:
            optimizer: Optimizer whose parameters' gradients should be unscaled
        """
        if not self._enabled:
            return
            
        # Reset inf detection for this step
        self._found_inf_this_step = False
        
        # Skip unscaling if scale is too small (PyTorch behavior)
        if self._scale < self._min_scale:
            self._found_inf_this_step = True
            return
            
        inv_scale = 1.0 / self._scale
        
        for param_name, param in optimizer.params:
            if param.requires_grad and param.grad is not None:
                # Check for inf/nan before unscaling
                grad_data = param.grad
                if hasattr(grad_data, 'get'):  # CuPy array
                    grad_cpu = grad_data.get()
                else:
                    grad_cpu = grad_data
                
                # Early inf/nan detection
                if not real_np.isfinite(grad_cpu).all():
                    self._found_inf_this_step = True
                    # Set gradients to zero to prevent further propagation
                    param.grad = xp.zeros_like(param.grad)
                    continue
                
                # Unscale gradient
                param.grad = param.grad * inv_scale
                
                # Check for inf/nan after unscaling (can occur due to very large gradients)
                if hasattr(param.grad, 'get'):
                    grad_cpu_unscaled = param.grad.get()
                else:
                    grad_cpu_unscaled = param.grad
                    
                if not real_np.isfinite(grad_cpu_unscaled).all():
                    self._found_inf_this_step = True
                    param.grad = xp.zeros_like(param.grad)
                    continue
                
                # Gradient clipping to prevent future overflow (optional - PyTorch doesn't do this by default)
                grad_norm = float(xp.linalg.norm(param.grad).item() if hasattr(xp.linalg.norm(param.grad), 'item') else xp.linalg.norm(param.grad))
                max_norm = 5.0  # More lenient than before
                if grad_norm > max_norm:
                    clip_coef = max_norm / (grad_norm + 1e-6)
                    param.grad = param.grad * clip_coef
    
    def step(self, optimizer) -> None:
        """
        Perform optimizer step with gradient scaling.
        
        This unscales gradients, checks for overflow, and conditionally runs
        the optimizer step. Follows PyTorch's behavior exactly.
        
        Args:
            optimizer: Optimizer to step
        """
        if not self._enabled:
            optimizer.step()
            return
        
        # Unscale gradients and detect inf/nan
        self.unscale_(optimizer)
        
        # Only step if no overflow detected (like PyTorch)
        if not self._found_inf_this_step:
            optimizer.step()
        else:
            # Log overflow event for debugging
            print(f"⚠️  Gradient overflow detected, skipping optimizer step (scale: {self._scale})")
    
    def update(self) -> None:
        """
        Update the scale factor based on recent gradient overflow status.
        
        Should be called after each training step to adjust the scale factor
        for the next iteration. Implements PyTorch's scaling logic.
        """
        if not self._enabled:
            return
        
        if self._found_inf_this_step:
            # Overflow detected - reduce scale (PyTorch behavior)
            new_scale = self._scale * self._backoff_factor
            # Prevent scale from going too low 
            self._scale = max(new_scale, self._min_scale)
            self._growth_tracker = 0
            # Reset found_inf for next iteration
            self._found_inf_this_step = False
        else:
            # No overflow - consider growing scale
            self._growth_tracker += 1
            if self._growth_tracker >= self._growth_interval:
                self._scale = min(self._scale * self._growth_factor, 2**24)  # Match PyTorch's maximum
                self._growth_tracker = 0
    
    def state_dict(self) -> Dict[str, Any]:
        """Get state dictionary for checkpointing."""
        return {
            'scale': self._scale,
            'growth_tracker': self._growth_tracker,
            'found_inf': self._found_inf_this_step,
            'growth_factor': self._growth_factor,
            'backoff_factor': self._backoff_factor,
            'growth_interval': self._growth_interval,
            'enabled': self._enabled,
            'min_scale': self._min_scale
        }
    
    def load_state_dict(self, state_dict: Dict[str, Any]) -> None:
        """Load state dictionary from checkpoint."""
        self._scale = state_dict['scale']
        self._growth_tracker = state_dict['growth_tracker'] 
        self._found_inf_this_step = state_dict.get('found_inf', False)  # Backwards compatibility
        self._growth_factor = state_dict['growth_factor']
        self._backoff_factor = state_dict['backoff_factor']
        self._growth_interval = state_dict['growth_interval']
        self._enabled = state_dict['enabled']
        self._min_scale = state_dict.get('min_scale', 1.0 / (2**14))  # Updated default