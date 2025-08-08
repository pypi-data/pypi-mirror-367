from typing import Union, List, Tuple
import tensorly as tl
import numpy as np
from tensorly import backend as T
from apollo_toolbox_py.apollo_py.extra_tensorly_backend import ExtraBackend as T2, Device, DType

__all__ = ['M', 'M3']


class M:
    def __init__(self, array: Union[List[List[float]], np.ndarray], device: Device = Device.CPU,
                 dtype: DType = DType.Float64):
        if tl.is_tensor(array):
            self.array = array
        elif T2.check_if_an_element_is_tensor(array):
            self.array = T2.new_from_heterogeneous_array(array)
        else:
            self.array = T2.new(array, device, dtype)

        assert len(self.array.shape) == 2

    def __getitem__(self, item):
        return self.array[item]

    def __setitem__(self, key, value):
        self.array = T2.set_and_return(self.array, key, value)

    def set_and_return(self, key, value):
        return self.__class__(T2.set_and_return(self.array, key, value))

    @property
    def T(self):
        return self.transpose()

    def transpose(self) -> 'M':
        return M(self.array.T)

    def det(self) -> float:
        return T2.det(self.array)

    def inv(self) -> 'M':
        return M(T2.inv(self.array))

    def pinv(self) -> 'M':
        return M(T2.pinv(self.array))

    def dot(self, other: Union['M', np.ndarray]) -> 'M':
        if isinstance(other, M):
            other = other.array
        return M(tl.dot(self.array, other))

    def trace(self) -> float:
        return tl.trace(self.array)

    def rank(self) -> int:
        return T2.matrix_rank(self.array)

    def eigvals(self) -> np.ndarray:
        return T2.eigvals(self.array)

    def svd(self, full_matrices: bool = False) -> Tuple['M', np.ndarray, 'M']:
        U, S, V = tl.svd(self.array, full_matrices=full_matrices)
        return M(U), S, M(V)

    def eig(self):
        eigenvalues, eigenvectors = T2.eig(self.array)
        return eigenvalues, M(eigenvectors)

    def __add__(self, other: Union['M', np.ndarray]) -> 'M':
        if isinstance(other, M):
            other = other.array
        return self.__class__(self.array + other)

    def __sub__(self, other: Union['M', np.ndarray]) -> 'M':
        if isinstance(other, M):
            other = other.array
        return self.__class__(self.array - other)

    def __mul__(self, scalar: float) -> 'M':
        return self.__class__(self.array * scalar)

    def __truediv__(self, scalar: float) -> 'M':
        if scalar == 0:
            raise ValueError("Division by zero is not allowed.")
        return self.__class__(self.array / scalar)

    def __rtruediv__(self, scalar: float) -> 'M':
        return self.__class__(scalar / self.array)

    def __matmul__(self, other: Union['M', np.ndarray]) -> 'M':
        if isinstance(other, M):
            other = other.array
        return self.__class__(tl.matmul(self.array, other))

    def __repr__(self) -> str:
        return f"Matrix(\n{self.array}\n)"

    def __str__(self) -> str:
        return f"Matrix(\n{self.array}\n)"


class M3(M):
    def __init__(self, array: Union[List[List[float]], np.ndarray], device: Device = Device.CPU,
                 dtype: DType = DType.Float64):
        super().__init__(array, device, dtype)
        if self.array.shape != (3, 3):
            raise ValueError("Matrix3 must be a 3x3 matrix.")

    def __repr__(self) -> str:
        return f"Matrix3(\n{self.array}\n)"

    def __str__(self) -> str:
        return f"Matrix3(\n{self.array}\n)"
