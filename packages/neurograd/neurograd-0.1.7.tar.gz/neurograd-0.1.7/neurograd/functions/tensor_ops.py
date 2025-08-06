from neurograd import xp
from .base import Function
from neurograd.nn.module import Module
from typing import TYPE_CHECKING, Union, Tuple, Sequence
from numpy.typing import ArrayLike
if TYPE_CHECKING:
    from neurograd.tensor import Tensor



class Reshape(Function, Module):
    name = "Reshape"
    """Reshape tensor to new shape"""
    def __init__(self, new_shape):
        Function.__init__(self)
        Module.__init__(self)
        self.new_shape = new_shape
        self.original_shape = None
    def forward(self, A: xp.ndarray) -> xp.ndarray:
        self.original_shape = A.shape
        return xp.reshape(A, self.new_shape)
    def backward(self, grad_output: xp.ndarray) -> xp.ndarray:
        A = self.parent_tensors[0]
        return xp.reshape(grad_output, self.original_shape) if A.requires_grad else None


class Flatten(Function, Module):
    name = "Flatten"
    """Flatten tensor to 1D"""
    def __init__(self):
        Function.__init__(self)
        Module.__init__(self)
    def forward(self, A: xp.ndarray) -> xp.ndarray:
        # Flatten all dimensions except the first (batch) dimension
        return A.reshape(A.shape[0], -1)
    def backward(self, grad_output: xp.ndarray) -> xp.ndarray:
        A = self.parent_tensors[0]
        return grad_output.reshape(A.shape) if A.requires_grad else None


class Squeeze(Function, Module):
    name = "Squeeze"
    """Remove dimensions of size 1 from tensor"""
    def __init__(self, axes=None):
        Function.__init__(self)
        Module.__init__(self)
        self.axes = axes
    def forward(self, A: xp.ndarray) -> xp.ndarray:
        return xp.squeeze(A, axis=self.axes)
    def backward(self, grad_output: xp.ndarray) -> xp.ndarray:
        A = self.parent_tensors[0]
        return grad_output.reshape(A.shape) if A.requires_grad else None


class ExpandDims(Function, Module):
    name = "ExpandDims"
    """Add new axis of size 1 at specified position"""
    def __init__(self, axis):
        Function.__init__(self)
        Module.__init__(self)
        self.axis = axis
        self.original_shape = None
    def forward(self, A: xp.ndarray) -> xp.ndarray:
        self.original_shape = A.shape
        return xp.expand_dims(A, axis=self.axis)
    def backward(self, grad_output: xp.ndarray) -> xp.ndarray:
        A = self.parent_tensors[0]
        return xp.squeeze(grad_output, axis=self.axis) if A.requires_grad else None
    

class Pad(Function, Module):
    name = "Pad"
    """Pad tensor with zeros or specified value"""
    
    def __init__(self, pad_width: Union[Sequence, ArrayLike, int], mode='constant', 
                 constant_values=0, **kwargs):
        self.pad_width_input = pad_width
        self.mode = mode
        self.constant_values = constant_values
        self.kwargs = kwargs
    
    def forward(self, A: xp.ndarray) -> xp.ndarray:
        # Normalize pad_width based on tensor dimensions
        if isinstance(self.pad_width_input, int):
            pad_width = [(self.pad_width_input, self.pad_width_input)] * A.ndim
        elif isinstance(self.pad_width_input, Sequence) and isinstance(self.pad_width_input[0], int):
            pad_width = [(p, p) for p in self.pad_width_input]
        else:
            pad_width = list(self.pad_width_input)
        
        self.pad_width = pad_width
        return xp.pad(A, pad_width=self.pad_width, mode=self.mode, 
                      constant_values=self.constant_values, **self.kwargs)
    
    def backward(self, grad_output: xp.ndarray) -> xp.ndarray:
        A = self.parent_tensors[0]
        if not A.requires_grad:
            return None
        
        slices = []
        for lower, upper in self.pad_width:
            if upper == 0:
                slices.append(slice(lower, None))
            else:
                slices.append(slice(lower, -upper))
        return grad_output[tuple(slices)]



class SlidingWindowView(Function, Module):
    """
    Smart Vectorized Sliding Window View with AutoDiff Support 
    """
    def __init__(self, window_shape: Sequence[int], axes: Union[int, Tuple[int, ...]] = (2, 3), 
                 strides: Union[int, Tuple[int, ...]] = (1, 1)):
        Function.__init__(self)
        Module.__init__(self)
        self.window_shape = window_shape
        self.axes = axes if isinstance(axes, tuple) else tuple(axes)
        self.strides = strides if isinstance(strides, tuple) else \
                       tuple(strides for _ in range(len(axes)))
        self.grad_input = None
        self.grad_input_view = None
    def forward(self, A: xp.ndarray) -> xp.ndarray:
        from neurograd import xp
        sliding_window_view = xp.lib.stride_tricks.sliding_window_view
        # Reset input grad
        self.grad_input = xp.zeros_like(A)
        slices = [slice(None)] * A.ndim
        for ax, stride in zip(self.axes, self.strides):
            slices[ax] = slice(None, None, stride)
        slices = tuple(slices)
        input_view = sliding_window_view(A, self.window_shape, self.axes)[slices]
        self.grad_input_view = sliding_window_view(self.grad_input, self.window_shape, self.axes)[slices]
        return input_view
    def backward(self, grad_output):
        self.grad_input_view += grad_output
        return self.grad_input


def reshape(A, new_shape):
    return Reshape(new_shape)(A)
def flatten(A):
    return Flatten()(A)
def squeeze(A, axes=None):
    return Squeeze(axes)(A)
def expand_dims(A, axis):
    return ExpandDims(axis)(A)
def pad(A, pad_width, mode='constant', constant_values=0, **kwargs):
    return Pad(pad_width, mode, constant_values, **kwargs)(A)
def sliding_window_view(A, window_shape: Sequence[int], axes: Union[int, Tuple[int, ...]] = (2, 3), 
                        strides: Union[int, Tuple[int, ...]] = (1, 1)):
    return SlidingWindowView(window_shape, axes, strides)(A)

# newaxis constant for numpy-style indexing
newaxis = None
    