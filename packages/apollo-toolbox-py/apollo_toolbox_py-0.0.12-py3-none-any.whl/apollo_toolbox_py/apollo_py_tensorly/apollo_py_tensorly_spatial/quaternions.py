from typing import Union, List

import numpy as np

from apollo_toolbox_py.apollo_py_tensorly.apollo_py_tensorly_linalg.vectors import V, V4, V3
import tensorly as tl
from tensorly import backend as T
from apollo_toolbox_py.apollo_py.extra_tensorly_backend import ExtraBackend as T2, Device, DType
import copy


class Quaternion:
    def __init__(self, wxyz_array: Union[List[float], np.ndarray, V4], device: Device = Device.CPU,
                 dtype: DType = DType.Float64):
        if isinstance(wxyz_array, Quaternion):
            self.array = wxyz_array.array
            return

        if isinstance(wxyz_array, V4):
            self.array = wxyz_array
            return
        # super().__init__(wxyz_array, device, dtype)
        self.array = V4(wxyz_array, device, dtype)

    def __getitem__(self, item):
        return self.array[item]

    def __setitem__(self, key, value):
        self.array[key] = value

    @property
    def w(self):
        return self.array[0]

    @property
    def x(self):
        return self.array[1]

    @property
    def y(self):
        return self.array[2]

    @property
    def z(self):
        return self.array[3]

    def conjugate(self) -> 'Quaternion':
        # w, x, y, z = self.array
        w = self.array[0]
        x = self.array[1]
        y = self.array[2]
        z = self.array[3]
        out = Quaternion(
            tl.tensor([1., 0., 0., 0.], device=getattr(self.array.array, "device", None), dtype=self.array.array.dtype))
        out[0] = w
        out[1] = -x
        out[2] = -y
        out[3] = -z
        return out

    def inverse(self):
        conjugate = self.conjugate()
        norm_sq = self.array.norm() ** 2
        return Quaternion(conjugate.array / norm_sq)

    def to_unit_quaternion(self) -> 'UnitQuaternion':
        return UnitQuaternion(self.array, auto_normalize=True)

    def __mul__(self, other: 'Quaternion') -> 'Quaternion':
        w1, x1, y1, z1 = self.array[0], self.array[1], self.array[2], self.array[3]
        w2, x2, y2, z2 = other.array[0], other.array[1], other.array[2], other.array[3]

        out = Quaternion(
            tl.tensor([1., 0., 0., 0.], device=getattr(self.array.array, "device", None), dtype=self.array.array.dtype))
        out[0] = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
        out[1] = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
        out[2] = w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2
        out[3] = w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2

        return out

    def __matmul__(self, other: 'Quaternion') -> 'Quaternion':
        return self * other

    def __repr__(self) -> str:
        return f"Quaternion(\n{self.array.array}\n)"

    def __str__(self) -> str:
        return f"Quaternion(\n{self.array.array}\n)"


class UnitQuaternion(Quaternion):
    def __init__(self, wxyz_array: Union[List[float], np.ndarray, V4], device: Device = Device.CPU,
                 dtype: DType = DType.Float64, auto_normalize=True):
        if isinstance(wxyz_array, UnitQuaternion):
            self.array = wxyz_array.array
        else:
            super().__init__(wxyz_array, device, dtype)

        if auto_normalize:
            self.array = self.array.normalize()
        else:
            assert T2.allclose(self.array.norm(), 1.0)

    def __setitem__(self, key, value):
        raise NotImplementedError('__setitem__ is not supported on UnitQuaternions')

    @staticmethod
    def new_random_with_range(minimum=-1.0, maximum=1.0, device: Device = Device.CPU,
                              dtype: DType = DType.Float64):
        v = V3.new_random_with_range(minimum, maximum, device, dtype)
        return UnitQuaternion.from_euler_angles(v)

    @classmethod
    def from_euler_angles(cls, xyz: V3) -> 'UnitQuaternion':
        cy = tl.cos(xyz[2] * 0.5)
        sy = tl.sin(xyz[2] * 0.5)
        cp = tl.cos(xyz[1] * 0.5)
        sp = tl.sin(xyz[1] * 0.5)
        cr = tl.cos(xyz[0] * 0.5)
        sr = tl.sin(xyz[0] * 0.5)

        w = cr * cp * cy + sr * sp * sy
        x = sr * cp * cy - cr * sp * sy
        y = cr * sp * cy + sr * cp * sy
        z = cr * cp * sy - sr * sp * cy

        out = Quaternion(tl.tensor([1., 0., 0., 0.], device=getattr(xyz.array, "device", None), dtype=xyz.array.dtype))
        out[0] = w
        out[1] = x
        out[2] = y
        out[3] = z

        return out.to_unit_quaternion()

    @classmethod
    def from_axis_angle(cls, axis: V3, angle) -> 'UnitQuaternion':
        scaled_axis = axis.normalize()
        scaled_axis = scaled_axis * angle
        return UnitQuaternion.from_scaled_axis(scaled_axis)

    @classmethod
    def from_scaled_axis(cls, scaled_axis: V3) -> 'UnitQuaternion':
        norm = scaled_axis.norm()

        half_angle = norm / 2.0
        sin_half_angle = tl.sin(half_angle)
        cos_half_angle = tl.cos(half_angle)

        out = Quaternion(tl.tensor([1., 0., 0., 0.], device=getattr(scaled_axis.array, "device", None),
                                   dtype=scaled_axis.array.dtype))

        if norm < 1e-8:
            out[0] = cos_half_angle
            out[1] = sin_half_angle * 0.0
            out[2] = sin_half_angle * 0.0
            out[3] = sin_half_angle * 0.0
        else:
            a = scaled_axis / norm

            out[0] = cos_half_angle
            out[1] = sin_half_angle * a[0]
            out[2] = sin_half_angle * a[1]
            out[3] = sin_half_angle * a[2]

        return out.to_unit_quaternion()

    def conjugate(self) -> 'UnitQuaternion':
        return super().conjugate().to_unit_quaternion()

    def inverse(self) -> 'UnitQuaternion':
        return self.conjugate()

    def to_rotation_matrix(self) -> 'Rotation3':
        from apollo_toolbox_py.apollo_py_tensorly.apollo_py_tensorly_spatial.rotation_matrices import Rotation3
        w, x, y, z = self[0], self[1], self[2], self[3]
        matrix = [
            [1 - 2 * (y ** 2 + z ** 2), 2 * (x * y - z * w), 2 * (x * z + y * w)],
            [2 * (x * y + z * w), 1 - 2 * (x ** 2 + z ** 2), 2 * (y * z - x * w)],
            [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x ** 2 + y ** 2)]
        ]
        return Rotation3(T2.new_from_heterogeneous_array(matrix))

    def map_point(self, v: V3) -> 'V3':
        qv = Quaternion(tl.tensor([0., 0., 0., 0.], device=getattr(v.array, "device", None), dtype=v.array.dtype))
        qv[1] = v.array[0]
        qv[2] = v.array[1]
        qv[3] = v.array[2]

        res = self @ qv @ self.conjugate()

        out = V3(tl.tensor([0., 0., 0.], device=getattr(v.array, "device", None), dtype=v.array.dtype))
        out[0] = res[1]
        out[1] = res[2]
        out[2] = res[3]
        return out

    def to_lie_group_h1(self) -> 'LieGroupH1':
        from apollo_toolbox_py.apollo_py_tensorly.apollo_py_tensorly_spatial.lie.h1 import LieGroupH1
        return LieGroupH1(self.array)

    def __mul__(self, other: Union['UnitQuaternion', 'Quaternion']) -> Union['UnitQuaternion', 'Quaternion']:
        tmp = super().__mul__(other)
        if isinstance(other, UnitQuaternion):
            qq = UnitQuaternion(tl.tensor([1., 0., 0., 0.], device=getattr(self.array.array, "device", None),
                                          dtype=self.array.array.dtype))
            qq.array = tmp.array
            return qq
        else:
            return tmp

    def __matmul__(self, other: Union['UnitQuaternion', 'Quaternion']) -> Union['UnitQuaternion', 'Quaternion']:
        return self * other

    def __repr__(self) -> str:
        return f"UnitQuaternion(\n{self.array.array}\n)"

    def __str__(self) -> str:
        return f"UnitQuaternion(\n{self.array.array}\n)"
