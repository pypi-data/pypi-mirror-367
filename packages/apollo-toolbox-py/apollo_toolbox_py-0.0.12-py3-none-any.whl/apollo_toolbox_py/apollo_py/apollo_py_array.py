'''

from typing import TypeVar, Optional, Union, Tuple
import numpy as np
import scipy

try:
    import jax.numpy as jnp
    import jax.scipy as jsp
    import jax

    HAS_JAX = True
except ImportError:
    HAS_JAX = False

try:
    import torch

    HAS_PYTORCH = True
except ImportError:
    HAS_PYTORCH = False

T = TypeVar('T', bound='ApolloPyArrayABC')
B = TypeVar('B', bound='ApolloPyArrayBackend')


class ApolloPyArray:
    def __init__(self):
        self.array = None
        self.backend = None

    @classmethod
    def new_with_backend(cls, row_major_values, backend: B = None) -> 'ApolloPyArray':
        if not backend:
            backend = ApolloPyArrayBackendNumpy()

        if isinstance(row_major_values, ApolloPyArray):
            row_major_values = row_major_values.to_numpy_array()

        out = cls()
        out.array = backend.create_array(row_major_values)
        out.backend = backend
        return out

    @classmethod
    def new(cls, array, backend: B) -> 'ApolloPyArray':
        if isinstance(array, np.ndarray):
            return cls.new_with_backend(array, backend)

        assert issubclass(type(array), ApolloPyArrayABC) or isinstance(array,
                                                                       ApolloPyArray), 'array is of type {}.  You should probably use new_with_backend'.format(
            type(array))

        if not backend:
            backend = ApolloPyArrayBackendNumpy()

        if isinstance(array, ApolloPyArray):
            array = array.array

        out = cls()
        out.array = array
        out.backend = backend
        return out

    @staticmethod
    def zeros(shape, backend: B = None) -> 'ApolloPyArray':
        if not backend:
            backend = ApolloPyArrayBackendNumpy()
        a = np.zeros(shape)
        return ApolloPyArray.new_with_backend(a, backend)

    @staticmethod
    def ones(shape, backend: B = None) -> 'ApolloPyArray':
        if not backend:
            backend = ApolloPyArrayBackendNumpy()
        a = np.ones(shape)
        return ApolloPyArray.new_with_backend(a, backend)

    @staticmethod
    def diag(diag, backend: B = None) -> 'ApolloPyArray':
        if not backend:
            backend = ApolloPyArrayBackendNumpy()
        a = np.diag(diag)
        return ApolloPyArray.new_with_backend(a, backend)

    def mul(self, other: 'ApolloPyArray') -> 'ApolloPyArray':
        return ApolloPyArray.new(self.array @ other.array, self.backend)

    def __matmul__(self, other: 'ApolloPyArray') -> 'ApolloPyArray':
        return self.mul(other)

    def add(self, other) -> 'ApolloPyArray':
        if isinstance(other, ApolloPyArray):
            return ApolloPyArray.new(self.array + other.array, self.backend)
        else:
            other = ApolloPyArray.new(self.backend.create_array(other), self.backend)
            return self.add(other)

    def __add__(self, other) -> 'ApolloPyArray':
        return self.add(other)

    def sub(self, other: 'ApolloPyArray') -> 'ApolloPyArray':
        if isinstance(other, ApolloPyArray):
            return ApolloPyArray.new(self.array - other.array, self.backend)
        else:
            other = ApolloPyArray.new(self.backend.create_array(other), self.backend)
            return self.sub(other)

    def __sub__(self, other: 'ApolloPyArray') -> 'ApolloPyArray':
        return self.sub(other)

    def scalar_mul(self, scalar) -> 'ApolloPyArray':
        if isinstance(scalar, ApolloPyArray):
            assert scalar.is_scalar()
            scalar = scalar.array.array
        return ApolloPyArray.new(scalar * self.array, self.backend)

    def __mul__(self, scalar) -> 'ApolloPyArray':
        return self.scalar_mul(scalar)

    def __rmul__(self, scalar) -> 'ApolloPyArray':
        return self.scalar_mul(scalar)

    def __neg__(self) -> 'ApolloPyArray':
        return ApolloPyArray.new(-1.0 * self.array, self.backend)

    def scalar_div(self, scalar) -> 'ApolloPyArray':
        if isinstance(scalar, ApolloPyArray):
            assert scalar.is_scalar()
            scalar = scalar.array.array
        return ApolloPyArray.new(self.array / scalar, self.backend)

    def __truediv__(self, scalar) -> 'ApolloPyArray':
        return self.scalar_div(scalar)

    def __pow__(self, scalar) -> 'ApolloPyArray':
        if isinstance(scalar, ApolloPyArray):
            assert scalar.is_scalar()
            scalar = scalar.array.array
        return self.power(scalar)

    def transpose(self) -> 'ApolloPyArray':
        return ApolloPyArray.new(self.array.transpose(), self.backend)

    @property
    def T(self):
        return self.transpose()

    def resize(self, new_shape: Tuple[int, ...]) -> 'ApolloPyArray':
        return ApolloPyArray.new(self.array.resize(new_shape), self.backend)

    @property
    def shape(self):
        return self.array.array.shape

    def is_scalar(self):
        return len(self.shape) == 0

    def diagonalize(self) -> 'ApolloPyArray':
        return ApolloPyArray.new(self.array.diagonalize(), self.backend)

    def inv(self) -> 'ApolloPyArray':
        return ApolloPyArray.new(self.array.inv(), self.backend)

    def pinv(self) -> 'ApolloPyArray':
        return ApolloPyArray.new(self.array.pinv(), self.backend)

    def det(self) -> 'ApolloPyArray':
        return ApolloPyArray.new(self.array.det(), self.backend)

    def matrix_rank(self) -> int:
        return self.array.matrix_rank()

    def trace(self) -> 'ApolloPyArray':
        return ApolloPyArray.new(self.array.trace(), self.backend)

    def matrix_exp(self) -> 'ApolloPyArray':
        return ApolloPyArray.new(self.array.matrix_exp(), self.backend)

    def l1_norm(self) -> 'ApolloPyArray':
        return ApolloPyArray.new(self.array.l1_norm(), self.backend)

    def linf_norm(self) -> 'ApolloPyArray':
        return ApolloPyArray.new(self.array.linf_norm(), self.backend)

    def p_norm(self, p) -> 'ApolloPyArray':
        return ApolloPyArray.new(self.array.p_norm(p), self.backend)

    def dot(self, other: 'ApolloPyArray') -> 'ApolloPyArray':
        return ApolloPyArray.new(self.array.dot(other.array), self.backend)

    # def svd(self, full_matrices: bool = True) -> 'SVDResult':
    #     return self.array.svd(full_matrices)

    def to_numpy_array(self):
        return self.array.to_numpy_array()

    def cross(self, other: 'ApolloPyArray') -> 'ApolloPyArray':
        return ApolloPyArray.new(self.array.cross(other.array), self.backend)

    def sin(self) -> 'ApolloPyArray':
        return ApolloPyArray.new(self.array.sin(), self.backend)

    def cos(self) -> 'ApolloPyArray':
        return ApolloPyArray.new(self.array.cos(), self.backend)

    def tan(self) -> 'ApolloPyArray':
        return ApolloPyArray.new(self.array.tan(), self.backend)

    def arcsin(self) -> 'ApolloPyArray':
        return ApolloPyArray.new(self.array.arcsin(), self.backend)

    def arccos(self) -> 'ApolloPyArray':
        return ApolloPyArray.new(self.array.arccos(), self.backend)

    def arctan(self) -> 'ApolloPyArray':
        return ApolloPyArray.new(self.array.arctan(), self.backend)

    def sinh(self) -> 'ApolloPyArray':
        return ApolloPyArray.new(self.array.sinh(), self.backend)

    def cosh(self) -> 'ApolloPyArray':
        return ApolloPyArray.new(self.array.cosh(), self.backend)

    def tanh(self) -> 'ApolloPyArray':
        return ApolloPyArray.new(self.array.tanh(), self.backend)

    def exp(self) -> 'ApolloPyArray':
        return ApolloPyArray.new(self.array.exp(), self.backend)

    def log(self) -> 'ApolloPyArray':
        return ApolloPyArray.new(self.array.log(), self.backend)

    def log10(self) -> 'ApolloPyArray':
        return ApolloPyArray.new(self.array.log10(), self.backend)

    def sqrt(self) -> 'ApolloPyArray':
        return ApolloPyArray.new(self.array.sqrt(), self.backend)

    def abs(self) -> 'ApolloPyArray':
        return ApolloPyArray.new(self.array.abs(), self.backend)

    def floor(self) -> 'ApolloPyArray':
        return ApolloPyArray.new(self.array.floor(), self.backend)

    def ceil(self) -> 'ApolloPyArray':
        return ApolloPyArray.new(self.array.ceil(), self.backend)

    def power(self, exponent) -> 'ApolloPyArray':
        return ApolloPyArray.new(self.array.power(exponent), self.backend)

    def __eq__(self, other) -> bool:
        if isinstance(other, ApolloPyArray):
            n1 = self.to_numpy_array()
            n2 = other.to_numpy_array()
            if n1.shape != n2.shape:
                return False
            return (n1 == n2).all()
        else:
            return self.array == other

    def isclose(self, other, tol=1e-3) -> bool:
        if isinstance(other, ApolloPyArray):
            n1 = self.to_numpy_array()
            n2 = other.to_numpy_array()
            if n1.shape != n2.shape:
                return False
            return np.isclose(n1, n2, atol=tol).all()
        else:
            return self.array.allclose(other, tol)

    def __getitem__(self, index):
        return ApolloPyArray.new(self.array.__getitem__(index), self.backend)

    def __setitem__(self, index, value):
        if isinstance(value, ApolloPyArray):
            value = value.array
        self.array.__setitem__(index, value)

    def __str__(self):
        return self.array.__str__()

    def __repr__(self):
        return self.array.__repr__()

    def type(self):
        return type(self.array)

    def is_numpy(self):
        return self.type() == ApolloPyArrayNumpy

    def is_jax(self):
        return self.type() == ApolloPyArrayJAX

    def is_torch(self):
        return self.type() == ApolloPyArrayTorch

    def item(self) -> float:
        shape = self.shape
        if shape == ():
            return self.array.array.item()
        elif shape == (1, 1):
            return self.array.array.item()
        else:
            raise ValueError(f'Unexpected shape {shape}')

    def set_torch_requires_grad(self, requires_grad: bool):
        assert self.is_torch()
        self.array.array.requires_grad_(requires_grad)


class ApolloPyArrayBackend:
    def create_array(self, row_major_values) -> T:
        raise NotImplementedError('abstract base class')


class ApolloPyArrayBackendNumpy(ApolloPyArrayBackend):
    def create_array(self, row_major_values) -> 'ApolloPyArrayNumpy':
        if isinstance(row_major_values, float) or isinstance(row_major_values, int) or isinstance(row_major_values,
                                                                                                  np.float64) or isinstance(
            row_major_values, np.float32) or (
                isinstance(row_major_values, np.ndarray) and row_major_values.shape == ()):
            return ApolloPyArrayNumpy(np.array(row_major_values))

        if isinstance(row_major_values[0], list):
            num_rows = len(row_major_values)
            num_cols = len(row_major_values[0])
            array = np.zeros((num_rows, num_cols))
            out = ApolloPyArrayJAX(jnp.array(array))
            for i in range(num_rows):
                for j in range(num_cols):
                    if isinstance(row_major_values, ApolloPyArrayNumpy):
                        val = row_major_values[i, j]
                    elif isinstance(row_major_values, np.ndarray):
                        val = row_major_values[i, j]
                    elif isinstance(row_major_values, jnp.ndarray):
                        val = row_major_values[i, j]
                    elif isinstance(row_major_values, ApolloPyArray):
                        val = row_major_values[i, j]
                    elif isinstance(row_major_values, list):
                        val = row_major_values[i][j]
                    else:
                        raise ValueError('not a legal input')

                    if isinstance(val, ApolloPyArray):
                        val = val.array.array
                    elif isinstance(val, ApolloPyArrayNumpy):
                        val = val.array
                    elif isinstance(val, np.ndarray) or isinstance(val, jnp.ndarray) or isinstance(val,
                                                                                                   float) or isinstance(
                        val, int) or isinstance(val, np.float32) or isinstance(val, np.float64):
                        val = val
                    else:
                        raise ValueError('not a legal input', 'val is of type {}'.format(type(val)))

                    out[i, j] = val

            return out
        else:
            num_rows = len(row_major_values)
            array = np.zeros((num_rows,))
            out = ApolloPyArrayNumpy(array)

            for i in range(num_rows):
                val = row_major_values[i]

                if isinstance(val, ApolloPyArray):
                    val = val.array.array
                elif isinstance(val, ApolloPyArrayJAX):
                    val = val.array
                elif isinstance(val, np.ndarray) or isinstance(val, jnp.ndarray) or isinstance(val,
                                                                                               float) or isinstance(
                    val, int):
                    val = val
                else:
                    raise ValueError('not a legal input')

                out[i] = val

            return out


class ApolloPyArrayABC:
    def __init__(self, array):
        self.array = array

    def mul(self, other: T) -> T:
        raise NotImplementedError('abstract base class')

    def __matmul__(self, other: T) -> T:
        return self.mul(other)

    def add(self, other: T) -> T:
        raise NotImplementedError('abstract base class')

    def __add__(self, other: T) -> T:
        return self.add(other)

    def sub(self, other: T) -> T:
        raise NotImplementedError('abstract base class')

    def __sub__(self, other: T) -> T:
        return self.sub(other)

    def scalar_mul(self, scalar) -> T:
        raise NotImplementedError('abstract base class')

    def __mul__(self, scalar) -> T:
        return self.scalar_mul(scalar)

    def __rmul__(self, scalar) -> T:
        return self.scalar_mul(scalar)

    def scalar_div(self, scalar) -> T:
        raise NotImplementedError('abstract base class')

    def __truediv__(self, scalar) -> T:
        return self.scalar_div(scalar)

    def transpose(self) -> T:
        raise NotImplementedError('abstract base class')

    @property
    def T(self):
        return self.transpose()

    def resize(self, new_shape: Tuple[int, ...]) -> T:
        raise NotImplementedError('abstract base class')

    def diagonalize(self) -> T:
        raise NotImplementedError('abstract base class')

    def cross(self, other: T) -> T:
        raise NotImplementedError('abstract base class')

    def inv(self) -> T:
        raise NotImplementedError('abstract base class')

    def pinv(self) -> T:
        raise NotImplementedError('abstract base class')

    def det(self) -> T:
        raise NotImplementedError('abstract base class')

    def matrix_rank(self) -> int:
        raise NotImplementedError('abstract base class')

    def trace(self) -> T:
        raise NotImplementedError('abstract base class')

    def matrix_exp(self) -> T:
        raise NotImplementedError('abstract base class')

    def l1_norm(self):
        raise NotImplementedError('abstract base class')

    def linf_norm(self):
        raise NotImplementedError('abstract base class')

    def p_norm(self, p):
        raise NotImplementedError('abstract base class')

    def dot(self, other: T) -> T:
        raise NotImplementedError('abstract base class')

    def svd(self, full_matrices: bool = False) -> 'SVDResult':
        raise NotImplementedError('abstract base class')

    def to_numpy_array(self) -> np.ndarray:
        raise NotImplementedError('abstract base class')

    def sin(self) -> T:
        raise NotImplementedError('abstract base class')

    def cos(self) -> T:
        raise NotImplementedError('abstract base class')

    def tan(self) -> T:
        raise NotImplementedError('abstract base class')

    def arcsin(self) -> T:
        raise NotImplementedError('abstract base class')

    def arccos(self) -> T:
        raise NotImplementedError('abstract base class')

    def arctan(self) -> T:
        raise NotImplementedError('abstract base class')

    def sinh(self) -> T:
        raise NotImplementedError('abstract base class')

    def cosh(self) -> T:
        raise NotImplementedError('abstract base class')

    def tanh(self) -> T:
        raise NotImplementedError('abstract base class')

    def exp(self) -> T:
        raise NotImplementedError('abstract base class')

    def log(self) -> T:
        raise NotImplementedError('abstract base class')

    def log10(self) -> T:
        raise NotImplementedError('abstract base class')

    def sqrt(self) -> T:
        raise NotImplementedError('abstract base class')

    def abs(self) -> T:
        raise NotImplementedError('abstract base class')

    def floor(self) -> T:
        raise NotImplementedError('abstract base class')

    def ceil(self) -> T:
        raise NotImplementedError('abstract base class')

    def power(self, exponent) -> T:
        raise NotImplementedError('abstract base class')

    def __getitem__(self, key):
        raise NotImplementedError('abstract base class')

    def __setitem__(self, key, value):
        raise NotImplementedError('abstract base class')

    def __repr__(self):
        return self.array.__repr__()

    def __str__(self):
        return self.array.__str__()


class ApolloPyArrayNumpy(ApolloPyArrayABC):
    def __init__(self, array):
        super().__init__(np.array(array))

    def mul(self, other: 'ApolloPyArrayNumpy') -> 'ApolloPyArrayNumpy':
        return ApolloPyArrayNumpy(self.array @ other.array)

    def add(self, other: 'ApolloPyArrayNumpy') -> 'ApolloPyArrayNumpy':
        return ApolloPyArrayNumpy(self.array + other.array)

    def sub(self, other: 'ApolloPyArrayNumpy') -> 'ApolloPyArrayNumpy':
        return ApolloPyArrayNumpy(self.array - other.array)

    def scalar_mul(self, scalar) -> 'ApolloPyArrayNumpy':
        return ApolloPyArrayNumpy(self.array * scalar)

    def scalar_div(self, scalar) -> 'ApolloPyArrayNumpy':
        return ApolloPyArrayNumpy(self.array / scalar)

    def transpose(self) -> T:
        return ApolloPyArrayNumpy(self.array.transpose())

    def resize(self, new_shape: Tuple[int, ...]) -> 'ApolloPyArrayNumpy':
        """
        Resize the NumPy array to a new shape.

        Args:
            new_shape: A tuple representing the new shape of the array

        Returns:
            A new NumPy-backed ApolloPyArray with the specified shape
        """
        return ApolloPyArrayNumpy(np.resize(self.array, new_shape))

    def diagonalize(self) -> 'ApolloPyArrayNumpy':
        return ApolloPyArrayNumpy(np.diag(self.array))

    def inv(self) -> 'ApolloPyArrayNumpy':
        return ApolloPyArrayNumpy(np.linalg.inv(self.array))

    def pinv(self) -> 'ApolloPyArrayNumpy':
        return ApolloPyArrayNumpy(np.linalg.pinv(self.array))

    def det(self) -> 'ApolloPyArrayNumpy':
        return ApolloPyArrayNumpy(np.linalg.det(self.array))

    def matrix_rank(self) -> int:
        return np.linalg.matrix_rank(self.array)

    def trace(self) -> 'ApolloPyArrayNumpy':
        return ApolloPyArrayNumpy(np.linalg.trace(self.array))

    def matrix_exp(self) -> 'ApolloPyArrayNumpy':
        return ApolloPyArrayNumpy(scipy.linalg.expm(self.array))

    def l1_norm(self) -> 'ApolloPyArrayNumpy':
        return ApolloPyArrayNumpy(np.linalg.norm(self.array, ord=1))

    def linf_norm(self) -> 'ApolloPyArrayNumpy':
        return ApolloPyArrayNumpy(np.max(np.abs(self.array)))

    def p_norm(self, p) -> 'ApolloPyArrayNumpy':
        return ApolloPyArrayNumpy(np.linalg.norm(self.array, ord=p))

    def dot(self, other: 'ApolloPyArrayNumpy') -> 'ApolloPyArrayNumpy':
        return ApolloPyArrayNumpy(self.array.dot(other.array))

    # def svd(self, full_matrices: bool = False) -> 'SVDResult':
    #     U, S, VT = np.linalg.svd(self.array, full_matrices=full_matrices)
    #     U = ApolloPyArrayNumpy(U)
    #     S = ApolloPyArrayNumpy(S)
    #     VT = ApolloPyArrayNumpy(VT)
    #     return SVDResult(ApolloPyArray.new(U), ApolloPyArray.new(S), ApolloPyArray.new(VT))

    def to_numpy_array(self) -> np.ndarray:
        return self.array

    def cross(self, other: 'ApolloPyArrayNumpy') -> 'ApolloPyArrayNumpy':
        return ApolloPyArrayNumpy(np.cross(self.array, other.array))

    def sin(self) -> 'ApolloPyArrayNumpy':
        return ApolloPyArrayNumpy(np.sin(self.array))

    def cos(self) -> 'ApolloPyArrayNumpy':
        return ApolloPyArrayNumpy(np.cos(self.array))

    def tan(self) -> 'ApolloPyArrayNumpy':
        return ApolloPyArrayNumpy(np.tan(self.array))

    def arcsin(self) -> 'ApolloPyArrayNumpy':
        return ApolloPyArrayNumpy(np.arcsin(self.array))

    def arccos(self) -> 'ApolloPyArrayNumpy':
        return ApolloPyArrayNumpy(np.arccos(self.array))

    def arctan(self) -> 'ApolloPyArrayNumpy':
        return ApolloPyArrayNumpy(np.arctan(self.array))

    def sinh(self) -> 'ApolloPyArrayNumpy':
        return ApolloPyArrayNumpy(np.sinh(self.array))

    def cosh(self) -> 'ApolloPyArrayNumpy':
        return ApolloPyArrayNumpy(np.cosh(self.array))

    def tanh(self) -> 'ApolloPyArrayNumpy':
        return ApolloPyArrayNumpy(np.tanh(self.array))

    def exp(self) -> 'ApolloPyArrayNumpy':
        return ApolloPyArrayNumpy(np.exp(self.array))

    def log(self) -> 'ApolloPyArrayNumpy':
        return ApolloPyArrayNumpy(np.log(self.array))

    def log10(self) -> 'ApolloPyArrayNumpy':
        return ApolloPyArrayNumpy(np.log10(self.array))

    def sqrt(self) -> 'ApolloPyArrayNumpy':
        return ApolloPyArrayNumpy(np.sqrt(self.array))

    def abs(self) -> 'ApolloPyArrayNumpy':
        return ApolloPyArrayNumpy(np.abs(self.array))

    def floor(self) -> 'ApolloPyArrayNumpy':
        return ApolloPyArrayNumpy(np.floor(self.array))

    def ceil(self) -> 'ApolloPyArrayNumpy':
        return ApolloPyArrayNumpy(np.ceil(self.array))

    def power(self, exponent) -> 'ApolloPyArrayNumpy':
        return ApolloPyArrayNumpy(np.power(self.array, exponent))

    def __eq__(self, other) -> bool:
        if isinstance(other, ApolloPyArrayNumpy):
            n1 = self.to_numpy_array()
            n2 = other.to_numpy_array()
            if n1.shape != n2.shape:
                return False
            return (n1 == n2).all()
        else:
            try:
                n = self.to_numpy_array()
                return (n == other).all()
            except:
                return False

    def isclose(self, other, tol=1e-3) -> bool:
        if isinstance(other, ApolloPyArrayNumpy):
            n1 = self.to_numpy_array()
            n2 = other.to_numpy_array()
            if n1.shape != n2.shape:
                return False
            return np.isclose(n1, n2, atol=tol).all()
        else:
            try:
                n = self.to_numpy_array()
                return np.isclose(n, other, atol=tol).all()
            except:
                return False

    def __getitem__(self, key):
        return ApolloPyArrayNumpy(self.array[key])

    def __setitem__(self, key, value):
        if isinstance(value, ApolloPyArrayNumpy):
            value = value.array
        self.array[key] = value


if HAS_JAX:
    class ApolloPyArrayBackendJAX(ApolloPyArrayBackend):
        def __init__(self,
                     device: Optional[jax.Device] = None,
                     dtype: Optional[jnp.dtype] = None):
            """
            Initialize JAX backend with optional device and dtype specifications.

            Args:
                device: JAX device to place the array on (e.g., jax.devices()[0])
                dtype: Data type for the array (e.g., jnp.float32, jnp.float64)
            """
            self.device = device or jax.devices()[0]
            self.dtype = dtype

        def create_array(self, row_major_values) -> 'ApolloPyArrayJAX':
            if isinstance(row_major_values, float) or isinstance(row_major_values, int) or isinstance(row_major_values,
                                                                                                      np.float64) or isinstance(
                row_major_values, np.float32) or (
                    isinstance(row_major_values, np.ndarray) and row_major_values.shape == ()):
                return ApolloPyArrayJAX(jnp.array(row_major_values, device=self.device, dtype=self.dtype))

            if isinstance(row_major_values[0], list):
                num_rows = len(row_major_values)
                num_cols = len(row_major_values[0])
                array = jnp.zeros((num_rows, num_cols), dtype=self.dtype, device=self.device)
                out = ApolloPyArrayJAX(jnp.array(array, device=self.device, dtype=self.dtype))
                for i in range(num_rows):
                    for j in range(num_cols):
                        if isinstance(row_major_values, ApolloPyArrayJAX):
                            val = row_major_values[i, j]
                        elif isinstance(row_major_values, np.ndarray):
                            val = row_major_values[i, j]
                        elif isinstance(row_major_values, jnp.ndarray):
                            val = row_major_values[i, j]
                        elif isinstance(row_major_values, ApolloPyArray):
                            val = row_major_values[i, j]
                        elif isinstance(row_major_values, list):
                            val = row_major_values[i][j]
                        else:
                            raise ValueError('not a legal input')

                        if isinstance(val, ApolloPyArray):
                            val = val.array.array
                        elif isinstance(val, ApolloPyArrayJAX):
                            val = val.array
                        elif isinstance(val, np.ndarray) or isinstance(val, jnp.ndarray) or isinstance(val,
                                                                                                       float) or isinstance(
                            val, int) or isinstance(val, np.float32) or isinstance(val, np.float64):
                            val = val
                        else:
                            raise ValueError('not a legal input', 'val is of type {}'.format(type(val)))

                        out[i, j] = val

                return out
            else:
                num_rows = len(row_major_values)
                array = jnp.zeros((num_rows,), dtype=self.dtype, device=self.device)
                out = ApolloPyArrayJAX(array)

                for i in range(num_rows):
                    val = row_major_values[i]

                    if isinstance(val, ApolloPyArray):
                        val = val.array.array
                    elif isinstance(val, ApolloPyArrayJAX):
                        val = val.array
                    elif isinstance(val, np.ndarray) or isinstance(val, jnp.ndarray) or isinstance(val,
                                                                                                   float) or isinstance(
                        val, int):
                        val = val
                    else:
                        raise ValueError('not a legal input')

                    out[i] = val

                return out


    class ApolloPyArrayJAX(ApolloPyArrayABC):
        def __init__(self, array):
            super().__init__(jnp.array(array))

        def mul(self, other: 'ApolloPyArrayJAX') -> 'ApolloPyArrayJAX':
            return ApolloPyArrayJAX(self.array @ other.array)

        def add(self, other: 'ApolloPyArrayJAX') -> 'ApolloPyArrayJAX':
            return ApolloPyArrayJAX(self.array + other.array)

        def sub(self, other: 'ApolloPyArrayJAX') -> 'ApolloPyArrayJAX':
            return ApolloPyArrayJAX(self.array - other.array)

        def scalar_mul(self, scalar) -> 'ApolloPyArrayJAX':
            return ApolloPyArrayJAX(self.array * scalar)

        def scalar_div(self, scalar) -> 'ApolloPyArrayJAX':
            return ApolloPyArrayJAX(self.array / scalar)

        def transpose(self) -> T:
            return ApolloPyArrayJAX(self.array.transpose())

        def resize(self, new_shape: Tuple[int, ...]) -> 'ApolloPyArrayJAX':
            """
            Resize the JAX array to a new shape.

            Args:
                new_shape: A tuple representing the new shape of the array

            Returns:
                A new JAX-backed ApolloPyArray with the specified shape
            """
            return ApolloPyArrayJAX(jnp.resize(self.array, new_shape))

        def diagonalize(self) -> 'ApolloPyArrayJAX':
            return ApolloPyArrayJAX(jnp.diag(self.array))

        def inv(self) -> 'ApolloPyArrayJAX':
            return ApolloPyArrayJAX(jnp.linalg.inv(self.array))

        def pinv(self) -> 'ApolloPyArrayJAX':
            return ApolloPyArrayJAX(jnp.linalg.pinv(self.array))

        def det(self) -> 'ApolloPyArrayJAX':
            return ApolloPyArrayJAX(jnp.linalg.det(self.array))

        def matrix_rank(self) -> int:
            return jnp.linalg.matrix_rank(self.array)

        def trace(self) -> 'ApolloPyArrayJAX':
            return ApolloPyArrayJAX(jnp.linalg.trace(self.array))

        def matrix_exp(self) -> 'ApolloPyArrayJAX':
            return ApolloPyArrayJAX(jsp.linalg.expm(self.array))

        def l1_norm(self) -> 'ApolloPyArrayJAX':
            return ApolloPyArrayJAX(jnp.linalg.norm(self.array, ord=1))

        def linf_norm(self) -> 'ApolloPyArrayJAX':
            return ApolloPyArrayJAX(jnp.max(jnp.abs(self.array)))

        def p_norm(self, p) -> 'ApolloPyArrayJAX':
            return ApolloPyArrayJAX(jnp.linalg.norm(self.array, ord=p))

        def dot(self, other: 'ApolloPyArrayJAX') -> 'ApolloPyArrayJAX':
            return ApolloPyArrayJAX(self.array.dot(other.array))

        # def svd(self, full_matrices: bool = False) -> 'SVDResult':
        #     U, S, VT = jnp.linalg.svd(self.array, full_matrices=full_matrices)
        #     U = ApolloPyArrayJAX(U)
        #     S = ApolloPyArrayJAX(S)
        #     VT = ApolloPyArrayJAX(VT)
        #     return SVDResult(ApolloPyArray.new(U), ApolloPyArray.new(S), ApolloPyArray.new(VT))

        def to_numpy_array(self) -> np.ndarray:
            return np.array(self.array)

        def cross(self, other: 'ApolloPyArrayJAX') -> 'ApolloPyArrayJAX':
            return ApolloPyArrayJAX(jnp.cross(self.array, other.array))

        def sin(self) -> 'ApolloPyArrayJAX':
            return ApolloPyArrayJAX(jnp.sin(self.array))

        def cos(self) -> 'ApolloPyArrayJAX':
            return ApolloPyArrayJAX(jnp.cos(self.array))

        def tan(self) -> 'ApolloPyArrayJAX':
            return ApolloPyArrayJAX(jnp.tan(self.array))

        def arcsin(self) -> 'ApolloPyArrayJAX':
            return ApolloPyArrayJAX(jnp.arcsin(self.array))

        def arccos(self) -> 'ApolloPyArrayJAX':
            return ApolloPyArrayJAX(jnp.arccos(self.array))

        def arctan(self) -> 'ApolloPyArrayJAX':
            return ApolloPyArrayJAX(jnp.arctan(self.array))

        def sinh(self) -> 'ApolloPyArrayJAX':
            return ApolloPyArrayJAX(jnp.sinh(self.array))

        def cosh(self) -> 'ApolloPyArrayJAX':
            return ApolloPyArrayJAX(jnp.cosh(self.array))

        def tanh(self) -> 'ApolloPyArrayJAX':
            return ApolloPyArrayJAX(jnp.tanh(self.array))

        def exp(self) -> 'ApolloPyArrayJAX':
            return ApolloPyArrayJAX(jnp.exp(self.array))

        def log(self) -> 'ApolloPyArrayJAX':
            return ApolloPyArrayJAX(jnp.log(self.array))

        def log10(self) -> 'ApolloPyArrayJAX':
            return ApolloPyArrayJAX(jnp.log10(self.array))

        def sqrt(self) -> 'ApolloPyArrayJAX':
            return ApolloPyArrayJAX(jnp.sqrt(self.array))

        def abs(self) -> 'ApolloPyArrayJAX':
            return ApolloPyArrayJAX(jnp.abs(self.array))

        def floor(self) -> 'ApolloPyArrayJAX':
            return ApolloPyArrayJAX(jnp.floor(self.array))

        def ceil(self) -> 'ApolloPyArrayJAX':
            return ApolloPyArrayJAX(jnp.ceil(self.array))

        def power(self, exponent) -> 'ApolloPyArrayJAX':
            return ApolloPyArrayJAX(jnp.power(self.array, exponent))

        def __eq__(self, other) -> bool:
            if isinstance(other, ApolloPyArrayJAX):
                n1 = self.to_numpy_array()
                n2 = other.to_numpy_array()
                if n1.shape != n2.shape:
                    return False
                return (n1 == n2).all()
            else:
                try:
                    n = self.to_numpy_array()
                    return (n == other).all()
                except:
                    return False

        def isclose(self, other, tol=1e-3) -> bool:
            if isinstance(other, ApolloPyArrayJAX):
                n1 = self.to_numpy_array()
                n2 = other.to_numpy_array()
                if n1.shape != n2.shape:
                    return False
                return np.isclose(n1, n2, atol=tol).all()
            else:
                try:
                    n = self.to_numpy_array()
                    return np.isclose(n, other, atol=tol).all()
                except:
                    return False

        def __getitem__(self, key):
            return ApolloPyArrayJAX(self.array[key])

        def __setitem__(self, key, value):
            if isinstance(value, ApolloPyArrayJAX):
                value = value.array
            self.array = self.array.at[key].set_and_return(value)

if HAS_PYTORCH:
    class ApolloPyArrayBackendTorch(ApolloPyArrayBackend):
        def __init__(self,
                     device: Optional[Union[str, torch.device]] = None,
                     dtype: Optional[torch.dtype] = None):
            """
            Initialize PyTorch backend with optional device and dtype specifications.

            Args:
                device: Device to place the tensor on (e.g., 'cuda', 'cpu', torch.device('cuda:0'))
                dtype: Data type for the tensor (e.g., torch.float32, torch.float64)
            """
            self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
            self.dtype = dtype or torch.float64

        def create_array(self, row_major_values) -> 'ApolloPyArrayTorch':
            # return ApolloPyArrayTorch(
            #     torch.tensor(
            #         row_major_values,
            #         device=self.device,
            #         dtype=self.dtype
            #     )
            # )
            if isinstance(row_major_values, float) or isinstance(row_major_values, int) or isinstance(row_major_values,
                                                                                                      np.float64) or isinstance(
                row_major_values, np.float32) or (
                    isinstance(row_major_values, np.ndarray) and row_major_values.shape == ()):
                return ApolloPyArrayTorch(torch.tensor(row_major_values, device=self.device, dtype=self.dtype))

            if isinstance(row_major_values[0], list):
                num_rows = len(row_major_values)
                num_cols = len(row_major_values[0])
                array = torch.zeros((num_rows, num_cols), dtype=self.dtype, device=self.device)
                out = ApolloPyArrayTorch(array)
                for i in range(num_rows):
                    for j in range(num_cols):
                        if isinstance(row_major_values, ApolloPyArrayTorch):
                            val = row_major_values[i, j]
                        elif isinstance(row_major_values, np.ndarray):
                            val = row_major_values[i, j]
                        elif isinstance(row_major_values, jnp.ndarray):
                            val = row_major_values[i, j]
                        elif isinstance(row_major_values, ApolloPyArray):
                            val = row_major_values[i, j]
                        elif isinstance(row_major_values, list):
                            val = row_major_values[i][j]
                        else:
                            raise ValueError('not a legal input')

                        if isinstance(val, ApolloPyArray):
                            val = val.array.array
                        elif isinstance(val, ApolloPyArrayTorch):
                            val = val.array
                        elif isinstance(val, np.ndarray) or isinstance(val, jnp.ndarray) or isinstance(val,
                                                                                                       float) or isinstance(
                            val, int) or isinstance(val, np.float32) or isinstance(val, np.float64):
                            val = val
                        else:
                            raise ValueError('not a legal input', 'val is of type {}'.format(type(val)))

                        out[i, j] = val

                return out
            else:
                num_rows = len(row_major_values)
                array = torch.zeros((num_rows,), dtype=self.dtype, device=self.device)
                out = ApolloPyArrayTorch(array)

                for i in range(num_rows):
                    val = row_major_values[i]

                    if isinstance(val, ApolloPyArray):
                        val = val.array.array
                    elif isinstance(val, ApolloPyArrayTorch):
                        val = val.array
                    elif isinstance(val, np.ndarray) or isinstance(val, jnp.ndarray) or isinstance(val,
                                                                                                   float) or isinstance(
                        val, int):
                        val = val
                    else:
                        raise ValueError('not a legal input')

                    out[i] = val

                return out


    class ApolloPyArrayTorch(ApolloPyArrayABC):
        def __init__(self, array):
            super().__init__(array)

        def mul(self, other: 'ApolloPyArrayTorch') -> 'ApolloPyArrayTorch':
            return ApolloPyArrayTorch(self.array @ other.array)

        def add(self, other: 'ApolloPyArrayTorch') -> 'ApolloPyArrayTorch':
            return ApolloPyArrayTorch(self.array + other.array)

        def sub(self, other: 'ApolloPyArrayTorch') -> 'ApolloPyArrayTorch':
            return ApolloPyArrayTorch(self.array - other.array)

        def scalar_mul(self, scalar) -> 'ApolloPyArrayTorch':
            return ApolloPyArrayTorch(self.array * scalar)

        def scalar_div(self, scalar) -> 'ApolloPyArrayTorch':
            return ApolloPyArrayTorch(self.array / scalar)

        def transpose(self) -> 'ApolloPyArrayTorch':
            return ApolloPyArrayTorch(self.array.T)

        def resize(self, new_shape: Tuple[int, ...]) -> 'ApolloPyArrayTorch':
            """
            Resize the PyTorch tensor to a new shape.

            Args:
                new_shape: A tuple representing the new shape of the array

            Returns:
                A new PyTorch-backed ApolloPyArray with the specified shape
            """
            return ApolloPyArrayTorch(self.array.reshape(new_shape))

        def diagonalize(self) -> 'ApolloPyArrayTorch':
            return ApolloPyArrayTorch(torch.diag(self.array))

        def inv(self) -> 'ApolloPyArrayTorch':
            return ApolloPyArrayTorch(torch.linalg.inv(self.array))

        def pinv(self) -> 'ApolloPyArrayTorch':
            return ApolloPyArrayTorch(torch.linalg.pinv(self.array))

        def det(self) -> 'ApolloPyArrayTorch':
            return ApolloPyArrayTorch(self.array.det())

        def matrix_rank(self) -> int:
            return torch.linalg.matrix_rank(self.array).item()

        def trace(self) -> 'ApolloPyArrayTorch':
            return ApolloPyArrayTorch(self.array.trace())

        def matrix_exp(self) -> 'ApolloPyArrayTorch':
            return ApolloPyArrayTorch(torch.linalg.matrix_exp(self.array))

        def l1_norm(self) -> 'ApolloPyArrayTorch':
            return ApolloPyArrayTorch(self.array.norm(ord=1))

        def linf_norm(self) -> 'ApolloPyArrayTorch':
            return ApolloPyArrayTorch(self.array.norm(torch.inf))

        def p_norm(self, p) -> 'ApolloPyArrayTorch':
            return ApolloPyArrayTorch(self.array.norm(p))

        def dot(self, other: 'ApolloPyArrayTorch') -> 'ApolloPyArrayTorch':
            return ApolloPyArrayTorch(torch.dot(self.array, other.array))

        # def svd(self, full_matrices: bool = False) -> 'SVDResult':
        #     U, S, VT = torch.linalg.svd(self.array, full_matrices=full_matrices)
        #     U = ApolloPyArrayTorch(U)
        #     S = ApolloPyArrayTorch(S)
        #     VT = ApolloPyArrayTorch(VT)
        #     return SVDResult(ApolloPyArray.new(U), ApolloPyArray.new(S), ApolloPyArray.new(VT))

        def to_numpy_array(self) -> np.ndarray:
            out = self.array.cpu().detach()

            return out.numpy()

        def cross(self, other: 'ApolloPyArrayTorch') -> 'ApolloPyArrayTorch':
            return ApolloPyArrayTorch(torch.cross(self.array, other.array, dim=0))

        def sin(self) -> 'ApolloPyArrayTorch':
            return ApolloPyArrayTorch(torch.sin(self.array))

        def cos(self) -> 'ApolloPyArrayTorch':
            return ApolloPyArrayTorch(torch.cos(self.array))

        def tan(self) -> 'ApolloPyArrayTorch':
            return ApolloPyArrayTorch(torch.tan(self.array))

        def arcsin(self) -> 'ApolloPyArrayTorch':
            return ApolloPyArrayTorch(torch.arcsin(self.array))

        def arccos(self) -> 'ApolloPyArrayTorch':
            return ApolloPyArrayTorch(torch.arccos(self.array))

        def arctan(self) -> 'ApolloPyArrayTorch':
            return ApolloPyArrayTorch(torch.arctan(self.array))

        def sinh(self) -> 'ApolloPyArrayTorch':
            return ApolloPyArrayTorch(torch.sinh(self.array))

        def cosh(self) -> 'ApolloPyArrayTorch':
            return ApolloPyArrayTorch(torch.cosh(self.array))

        def tanh(self) -> 'ApolloPyArrayTorch':
            return ApolloPyArrayTorch(torch.tanh(self.array))

        def exp(self) -> 'ApolloPyArrayTorch':
            return ApolloPyArrayTorch(torch.exp(self.array))

        def log(self) -> 'ApolloPyArrayTorch':
            return ApolloPyArrayTorch(torch.log(self.array))

        def log10(self) -> 'ApolloPyArrayTorch':
            return ApolloPyArrayTorch(torch.log10(self.array))

        def sqrt(self) -> 'ApolloPyArrayTorch':
            return ApolloPyArrayTorch(torch.sqrt(self.array))

        def abs(self) -> 'ApolloPyArrayTorch':
            return ApolloPyArrayTorch(torch.abs(self.array))

        def floor(self) -> 'ApolloPyArrayTorch':
            return ApolloPyArrayTorch(torch.floor(self.array))

        def ceil(self) -> 'ApolloPyArrayTorch':
            return ApolloPyArrayTorch(torch.ceil(self.array))

        def power(self, exponent) -> 'ApolloPyArrayTorch':
            return ApolloPyArrayTorch(torch.pow(self.array, exponent))

        def __eq__(self, other) -> bool:
            if isinstance(other, ApolloPyArrayTorch):
                n1 = self.to_numpy_array()
                n2 = other.to_numpy_array()
                if n1.shape != n2.shape:
                    return False
                return (n1 == n2).all()
            else:
                try:
                    n = self.to_numpy_array()
                    return (n == other).all()
                except:
                    return False

        def isclose(self, other, tol=1e-3) -> bool:
            if isinstance(other, ApolloPyArrayTorch):
                n1 = self.to_numpy_array()
                n2 = other.to_numpy_array()
                if n1.shape != n2.shape:
                    return False
                return np.isclose(n1, n2, atol=tol).all()
            else:
                try:
                    n = self.to_numpy_array()
                    return np.isclose(n, other, atol=tol).all()
                except:
                    return False

        def __getitem__(self, key):
            return ApolloPyArrayTorch(self.array[key])

        def __setitem__(self, key, value):
            if isinstance(value, ApolloPyArrayTorch):
                value = value.array
            if isinstance(value, torch.Tensor):
                self.array[key] = value
            else:
                self.array[key] = torch.tensor(value)


class SVDResult:
    def __init__(self, U: ApolloPyArray, singular_vals: ApolloPyArray, VT: ApolloPyArray):
        self.U = U
        self.singular_vals = singular_vals
        self.VT = VT
'''