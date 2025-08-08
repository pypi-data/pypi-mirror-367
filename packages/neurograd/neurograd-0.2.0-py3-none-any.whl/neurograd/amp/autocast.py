"""
Automatic Mixed Precision (AMP) Autocast Context Manager for NeuroGrad

This module provides autocast functionality that automatically converts operations
to FP16 when safe and keeps them in FP32 when precision is critical.
"""

import contextlib
from typing import Optional, Set
import neurograd as ng
from neurograd import xp
import threading

# Thread-local storage for autocast state
_autocast_state = threading.local()

# Operations that should remain in FP32 for numerical stability
FP32_OPS = {
    'Sum', 'Mean', 'Softmax', 'LogSoftmax', 'CategoricalCrossEntropy', 
    'BinaryCrossEntropy', 'BatchNorm2D', 'LayerNorm'
}

# Operations safe for FP16
FP16_OPS = {
    'Conv2D', 'Linear', 'ReLU', 'Add', 'Mul', 'MatMul', 'MaxPool2D'
}

def get_autocast_state():
    """Get current autocast state from thread-local storage"""
    return getattr(_autocast_state, 'enabled', False), getattr(_autocast_state, 'dtype', ng.float32)

def set_autocast_state(enabled: bool, dtype):
    """Set autocast state in thread-local storage"""
    _autocast_state.enabled = enabled
    _autocast_state.dtype = dtype

@contextlib.contextmanager
def autocast(enabled: bool = True, dtype=None):
    """
    Context manager for automatic mixed precision.
    
    Args:
        enabled (bool): Whether to enable autocast
        dtype: Target dtype for autocast (default: float16 if enabled)
    
    Example:
        with autocast():
            # Operations automatically use FP16 when safe
            output = model(input_tensor)
            loss = criterion(target, output)
        
        # Loss scaling handled separately in backward pass
        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()
    """
    if dtype is None:
        dtype = ng.float16 if enabled else ng.float32
    
    # Save previous state
    prev_enabled, prev_dtype = get_autocast_state()
    
    try:
        # Set new state
        set_autocast_state(enabled, dtype)
        yield
    finally:
        # Restore previous state
        set_autocast_state(prev_enabled, prev_dtype)

def should_autocast_op(op_name: str) -> bool:
    """
    Determine if an operation should be autocasted to FP16.
    
    Args:
        op_name: Name of the operation class
        
    Returns:
        bool: True if operation should be autocasted
    """
    enabled, _ = get_autocast_state()
    if not enabled:
        return False
    
    # Explicitly keep in FP32
    if op_name in FP32_OPS:
        return False
    
    # Safe for FP16
    if op_name in FP16_OPS:
        return True
    
    # Conservative default: keep in FP32 for unknown ops
    return False

def maybe_autocast_tensor(tensor, target_dtype=None):
    """
    Cast tensor to autocast dtype if autocast is enabled and safe.
    
    Args:
        tensor: Input tensor
        target_dtype: Optional target dtype override
        
    Returns:
        Tensor potentially cast to FP16
    """
    enabled, autocast_dtype = get_autocast_state()
    
    if not enabled:
        return tensor
    
    dtype = target_dtype if target_dtype is not None else autocast_dtype
    
    # Only cast if currently in FP32 and target is FP16
    if tensor.data.dtype == ng.float32 and dtype == ng.float16:
        return tensor.cast(dtype)
    
    return tensor

class AutocastFunction:
    """
    Mixin class for Functions to support autocast.
    
    Functions should inherit from this and call maybe_autocast_inputs()
    in their __call__ method.
    """
    
    def maybe_autocast_inputs(self, *inputs):
        """
        Autocast inputs if autocast is enabled and operation supports it.
        
        Args:
            *inputs: Input tensors
            
        Returns:
            Tuple of potentially autocast tensors
        """
        op_name = self.__class__.__name__
        
        if should_autocast_op(op_name):
            _, autocast_dtype = get_autocast_state()
            return tuple(maybe_autocast_tensor(inp, autocast_dtype) for inp in inputs)
        
        return inputs

# Monkey patch the Function base class to support autocast
def _enhanced_function_call(self, *inputs):
    """Enhanced __call__ method with autocast support"""
    from neurograd.tensor import Tensor
    
    # Convert inputs to tensors
    processed_inputs = []
    for i, inp in enumerate(inputs):
        if isinstance(inp, Tensor):
            processed_inputs.append(inp)
        else:
            try:
                data = xp.array(inp)
                processed_inputs.append(Tensor(data, requires_grad=False))
            except Exception as e:
                raise TypeError(f"Input {i} must be convertible to array, got {type(inp)}") from e
    
    # Apply autocast if this function supports it
    if hasattr(self, 'maybe_autocast_inputs'):
        processed_inputs = self.maybe_autocast_inputs(*processed_inputs)
    
    self.parent_tensors = processed_inputs
    output_data = self.forward(*[inp.data for inp in processed_inputs])
    requires_grad = any(inp.requires_grad for inp in processed_inputs)
    output = Tensor(output_data, requires_grad=requires_grad, grad_fn=self)
    return output

# Apply monkey patch
def enable_autocast_in_functions():
    """Enable autocast support in all Function classes"""
    from neurograd.functions.base import Function
    
    # Store original method
    if not hasattr(Function, '_original_call'):
        Function._original_call = Function.__call__
        Function.__call__ = _enhanced_function_call
    
    # Add autocast mixin to specific function classes
    function_modules = [
        'neurograd.functions.arithmetic',
        'neurograd.functions.linalg', 
        'neurograd.nn.layers.linear',
        'neurograd.nn.layers.conv'
    ]
    
    for module_name in function_modules:
        try:
            module = __import__(module_name, fromlist=[''])
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    hasattr(attr, 'forward') and 
                    hasattr(attr, 'backward')):
                    # Add autocast mixin
                    if not hasattr(attr, 'maybe_autocast_inputs'):
                        attr.maybe_autocast_inputs = AutocastFunction.maybe_autocast_inputs
        except ImportError:
            continue

# Initialize autocast support
enable_autocast_in_functions()
