import numpy as np


from apollo_toolbox_py.apollo_py_tensorly.apollo_py_tensorly_linalg.matrices import M3
from apollo_toolbox_py.apollo_py_tensorly.apollo_py_tensorly_linalg.vectors import V3
from apollo_toolbox_py.apollo_py_tensorly.apollo_py_tensorly_spatial.rotation_matrices import Rotation3
import tensorly as tl
from tensorly import backend as T
from apollo_toolbox_py.apollo_py.extra_tensorly_backend import ExtraBackend as T2, Device, DType

__all__ = ['LieGroupSO3', 'LieAlgSO3']


class LieGroupSO3(Rotation3):
    @classmethod
    def identity(cls, device: Device = Device.CPU, dtype: DType = DType.Float64) -> 'LieGroupSO3':
        return cls(np.identity(3), device, dtype)

    def ln(self) -> 'LieAlgSO3':
        m = self.array
        trace = tl.trace(m)
        mm = tl.clip(trace, -1.0, 1.0)
        beta = tl.arccos(mm)

        if T2.allclose(beta, 0.0):
            f = 0.5 + (beta ** 2 / 12.0) + (7.0 * beta ** 4 / 720.0)
            skew_symmetric = (m - m.T) * f
        elif T2.allclose(beta, tl.pi):
            r11 = tl.pi * tl.sqrt(0.5 * (m[0, 0] + 1.0))
            r22 = tl.pi * tl.sqrt(0.5 * (m[1, 1] + 1.0))
            r33 = tl.pi * tl.sqrt(0.5 * (m[2, 2] + 1.0))
            skew_symmetric = T2.new_from_heterogeneous_array([[0.0, -r33, r22], [r33, 0.0, -r11], [-r22, r11, 0.0]])
        else:
            f = beta / (2.0 * tl.sin(beta))
            skew_symmetric = (m - m.T) * f

        return LieAlgSO3(skew_symmetric)

    def __repr__(self) -> str:
        return f"LieGroupSO3(\n{self.array}\n)"

    def __str__(self) -> str:
        return f"LieGroupSO3(\n{self.array}\n)"


class LieAlgSO3(M3):
    @classmethod
    def from_euclidean_space_element(cls, e: V3) -> 'LieAlgSO3':
        skew_symmetric = T2.new_from_heterogeneous_array([[0, -e[2], e[1]], [e[2], 0, -e[0]], [-e[1], e[0], 0]])
        return cls(skew_symmetric)

    def exp(self) -> 'LieGroupSO3':
        u = T2.new_from_heterogeneous_array([self[2, 1], self[0, 2], self[1, 0]])
        beta = tl.norm(u)

        if T2.allclose(beta, 0.0):
            p = 1.0 - (beta ** 2 / 6.0) + (beta ** 4 / 120.0)
            q = 0.5 - (beta ** 2 / 24.0) + (beta ** 4 / 720.0)
        else:
            p = tl.sin(beta) / beta
            q = (1.0 - tl.cos(beta)) / (beta ** 2)

        rotation_matrix = tl.eye(3, device=getattr(u, "device", None), dtype=u.dtype) + p * self.array + q * (self.array @ self.array)
        return LieGroupSO3(rotation_matrix)

    def vee(self) -> V3:
        return V3(T2.new_from_heterogeneous_array([self[2, 1], self[0, 2], self[1, 0]]))

    def __repr__(self) -> str:
        return f"LieAlgSO3(\n{self.array}\n)"

    def __str__(self) -> str:
        return f"LieAlgSO3(\n{self.array}\n)"
