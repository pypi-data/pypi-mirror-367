import scipy
import tensorly as tl
from tensorly import backend as T
import numpy as np
from enum import Enum

try:
    import jax
    import jax.numpy as jnp
    import jax.scipy as jsp
except ImportError:
    jax = None
    jnp = None
    jsp = None

try:
    import torch
except ImportError:
    torch = None

__all__ = ['ExtraBackend', 'Device', 'DType', 'Backend']


class Device(Enum):
    CPU = 0
    MPS = 1
    CUDA = 2


class DType(Enum):
    Float32 = 0
    Float64 = 1


class Backend(Enum):
    Numpy = 0
    JAX = 1
    PyTorch = 2

    def to_string(self):
        if self == Backend.Numpy:
            return 'numpy'
        elif self == Backend.JAX:
            return 'jax'
        elif self == Backend.PyTorch:
            return 'pytorch'


class ExtraBackend:
    @staticmethod
    def new(array, device: Device = Device.CPU, dtype: DType = DType.Float64):
        b = T.get_backend()
        if b == 'numpy':
            if dtype == DType.Float64:
                d = np.float64
            elif dtype == DType.Float32:
                d = np.float32
            else:
                raise ValueError('Unsupported dtype')
            return tl.tensor(array, dtype=d)
        elif b == 'jax':
            if dtype == DType.Float64:
                d = np.float64
            elif dtype == DType.Float32:
                d = np.float32
            else:
                raise ValueError('Unsupported dtype')

            if device == Device.CPU:
                de = jax.devices("cpu")[0]
            elif device == Device.MPS or device == Device.CUDA:
                try:
                    de = jax.devices("gpu")[0]
                except:
                    print('gpu device not found for jax, defaulting to cpu')
                    de = jax.devices("cpu")[0]
            else:
                raise ValueError('Unsupported device')

            return tl.tensor(array, dtype=d, device=de)
        elif b == 'pytorch':
            if dtype == DType.Float64:
                d = torch.float64
            elif dtype == DType.Float32:
                d = torch.float32
            else:
                raise ValueError('Unsupported dtype')

            if device == Device.CPU:
                de = 'cpu'
            elif device == Device.MPS:
                de = 'mps'
            elif device == Device.CUDA:
                de = 'cuda'
            else:
                raise ValueError('Unsupported device')

            return tl.tensor(array, dtype=d, device=de)

    @staticmethod
    def check_if_an_element_is_tensor(array):
        flattened = flatten_nested_list(array)

        for e in flattened:
            if tl.is_tensor(e):
                return True
        return False

    @staticmethod
    def new_from_heterogeneous_array(array):
        shape = get_shape_of_nested_list(array)
        flattened = flatten_nested_list(array)

        device = None
        dtype = None
        for e in flattened:
            if tl.is_tensor(e):
                device = getattr(e, 'device', None)
                dtype = e.dtype
                break

        # assert device is not None and dtype is not None, 'this array does not have a tensor in it.  Probably just use regular new function'

        out = tl.zeros(shape, device=device, dtype=dtype)
        for (i, e) in enumerate(flattened):
            idxs = flat_index_to_nested(i, shape)
            out = ExtraBackend.set_and_return(out, tuple(idxs), e)

        return out

    @staticmethod
    def det(tl_tensor):
        b = T.get_backend()
        if b == 'numpy':
            return np.linalg.det(tl_tensor)
        elif b == 'jax':
            return jnp.linalg.det(tl_tensor)
        elif b == 'pytorch':
            return tl_tensor.det()
        else:
            raise ValueError(f'Backend {b} is not supported.')

    @staticmethod
    def expm(tl_tensor):
        b = T.get_backend()
        if b == 'numpy':
            return scipy.linalg.expm(tl_tensor)
        elif b == 'jax':
            return jsp.linalg.expm(tl_tensor)
        elif b == 'pytorch':
            return tl_tensor.matrix_exp()
        else:
            raise ValueError(f'Backend {b} is not supported.')

    @staticmethod
    def cross(tl_tensor1, tl_tensor2):
        b = T.get_backend()
        if b == 'numpy':
            return np.cross(tl_tensor1, tl_tensor2)
        elif b == 'jax':
            return jnp.cross(tl_tensor1, tl_tensor2)
        elif b == 'pytorch':
            return torch.linalg.cross(tl_tensor1, tl_tensor2)
        else:
            raise ValueError(f'Backend {b} is not supported.')

    @staticmethod
    def inv(tl_tensor):
        b = T.get_backend()
        if b == 'numpy':
            return np.linalg.inv(tl_tensor)
        elif b == 'jax':
            return jnp.linalg.inv(tl_tensor)
        elif b == 'pytorch':
            return torch.linalg.inv(tl_tensor)
        else:
            raise ValueError(f'Backend {b} is not supported.')

    @staticmethod
    def pinv(tl_tensor):
        b = T.get_backend()
        if b == 'numpy':
            return np.linalg.pinv(tl_tensor)
        elif b == 'jax':
            return jnp.linalg.pinv(tl_tensor)
        elif b == 'pytorch':
            return torch.linalg.pinv(tl_tensor)
        else:
            raise ValueError(f'Backend {b} is not supported.')

    @staticmethod
    def matrix_rank(tl_tensor):
        b = T.get_backend()
        if b == 'numpy':
            return np.linalg.matrix_rank(tl_tensor)
        elif b == 'jax':
            return jnp.linalg.matrix_rank(tl_tensor)
        elif b == 'pytorch':
            return torch.linalg.matrix_rank(tl_tensor)
        else:
            raise ValueError(f'Backend {b} is not supported.')

    @staticmethod
    def eig(tl_tensor):
        b = T.get_backend()
        if b == 'numpy':
            return np.linalg.eig(tl_tensor)
        elif b == 'jax':
            return jnp.linalg.eig(tl_tensor)
        elif b == 'pytorch':
            return torch.linalg.eig(tl_tensor)
        else:
            raise ValueError(f'Backend {b} is not supported.')

    @staticmethod
    def eigvals(tl_tensor):
        b = T.get_backend()
        if b == 'numpy':
            return np.linalg.eigvals(tl_tensor)
        elif b == 'jax':
            return jnp.linalg.eigvals(tl_tensor)
        elif b == 'pytorch':
            return torch.linalg.eigvals(tl_tensor)
        else:
            raise ValueError(f'Backend {b} is not supported.')

    @staticmethod
    def allclose(tl_tensor1, tl_tensor2, rtol=1e-05, atol=1e-05):
        tl_tensor1 = tl.to_numpy(tl_tensor1)
        tl_tensor2 = tl.to_numpy(tl_tensor2)
        return np.allclose(tl_tensor1, tl_tensor2, rtol=rtol, atol=atol)

    @staticmethod
    def arctan2(tl_tensor1, tl_tensor2):
        b = T.get_backend()
        if b == 'numpy':
            return np.arctan2(tl_tensor1, tl_tensor2)
        elif b == 'jax':
            return jnp.arctan2(tl_tensor1, tl_tensor2)
        elif b == 'pytorch':
            return torch.arctan2(tl_tensor1, tl_tensor2)
        else:
            raise ValueError(f'Backend {b} is not supported.')

    @staticmethod
    def min(tl_tensor1, tl_tensor2):
        if tl_tensor1 <= tl_tensor2:
            return tl_tensor1
        else:
            return tl_tensor2

    @staticmethod
    def max(tl_tensor1, tl_tensor2):
        if tl_tensor1 >= tl_tensor2:
            return tl_tensor1
        else:
            return tl_tensor2

    @staticmethod
    def set_and_return(tl_tensor, key, value):
        """
        for slices, make sure to use slice(), i.e., a : in traditional indexing can be replaced with slice(None)
        usage:

        a = T2.new([[1., 2.], [3., 4.]], Device.CPU, DType.Float64)
        a = T2.set(a, (slice(None), 1), 5.0)
        """
        b = T.get_backend()
        if b == 'numpy':
            tl_tensor[key] = value
        elif b == 'jax':
            tl_tensor = tl_tensor.at[key].set(value)
        elif b == 'pytorch':
            tl_tensor[key] = value
        else:
            raise ValueError(f'Backend {b} is not supported.')

        return tl_tensor


def get_shape_of_nested_list(nested_list):
    if isinstance(nested_list, list):
        return [len(nested_list)] + get_shape_of_nested_list(nested_list[0])
    else:
        return []


def flatten_nested_list(nested_list):
    result = []
    for item in nested_list:
        if isinstance(item, list):
            result.extend(flatten_nested_list(item))
        else:
            result.append(item)
    return result


def flat_index_to_nested(flat_index, shape):
    """
    Maps a flattened index to its corresponding indices in a nested list.

    Args:
        flat_index (int): The index in the flattened array.
        shape (tuple): The shape of the nested list (e.g., (2, 3, 4)).

    Returns:
        list: A list of indices corresponding to the nested dimensions.
    """
    indices = []
    for dim in reversed(shape):
        indices.append(flat_index % dim)  # Find index in the current dimension
        flat_index //= dim  # Update the flat index for the next dimension
    return list(reversed(indices))  # Reverse to match the original order


def nested_index_to_flat(nested_indices, shape):
    """
    Maps nested indices to a flattened index.

    Args:
        nested_indices (list): A list of indices corresponding to nested dimensions.
        shape (tuple): The shape of the nested list (e.g., (2, 3, 4)).

    Returns:
        int: The index in the flattened array.
    """
    flat_index = 0
    stride = 1
    for index, dim in zip(reversed(nested_indices), reversed(shape)):
        flat_index += index * stride
        stride *= dim
    return flat_index
