from apollo_toolbox_py.apollo_py.extra_tensorly_backend import ExtraBackend as T2, Device, DType
from apollo_toolbox_py.apollo_py_tensorly.apollo_py_tensorly_linalg.vectors import V3
from apollo_toolbox_py.apollo_py_tensorly.apollo_py_tensorly_spatial.quaternions import UnitQuaternion, Quaternion
import tensorly as tl

__all__ = ['LieGroupH1', 'LieAlgH1']


class LieGroupH1(UnitQuaternion):
    @classmethod
    def identity(cls, device: Device = Device.CPU, dtype: DType = DType.Float64) -> 'LieGroupH1':
        return cls([1., 0., 0., 0.], device, dtype)

    @classmethod
    def from_unit_quaternion(cls, quaternion: 'UnitQuaternion') -> 'LieGroupH1':
        return cls(quaternion)

    def group_operator(self, other: 'LieGroupH1') -> 'LieGroupH1':
        return LieGroupH1.from_unit_quaternion(self @ other)

    def ln(self):
        w, x, y, z = self[0], self[1], self[2], self[3]
        acos = tl.acos(T2.min(w, tl.tensor(1.0, device=getattr(w, "device", None), dtype=w.dtype)))
        if acos == 0.0:
            return LieAlgH1(T2.new_from_heterogeneous_array([0.0 * w, 0.0 * x, 0.0 * y, 0.0 * z]))
        else:
            ss = acos / tl.sin(acos)
            return LieAlgH1(T2.new_from_heterogeneous_array([0, ss * x, ss * y, ss * z]))

    def inverse(self) -> 'LieGroupH1':
        return LieGroupH1.from_unit_quaternion(self.conjugate())

    def displacement(self, other: 'LieGroupH1') -> 'LieGroupH1':
        return self.inverse().group_operator(other)

    def __repr__(self) -> str:
        return f"LieGroupH1(\n{self.array.array}\n)"

    def __str__(self) -> str:
        return f"LieGroupH1(\n{self.array.array}\n)"


class LieAlgH1(Quaternion):
    @classmethod
    def from_euclidean_space_element(cls, e: V3) -> 'LieAlgH1':
        return cls(T2.new_from_heterogeneous_array([0.0, e[0], e[1], e[2]]))

    def exp(self):
        v = V3(T2.new_from_heterogeneous_array([self[1], self[2], self[3]]))
        vn = v.norm()
        if vn == 0.0:
            cc = tl.cos(vn)
            return LieGroupH1(T2.new_from_heterogeneous_array([cc, 0.0 * v[0], 0.0 * v[1], 0.0 * v[2]]))
        else:
            cc = tl.cos(vn)
            ss = tl.sin(vn) / vn
            return LieGroupH1(T2.new_from_heterogeneous_array([cc, ss * v[0], ss * v[1], ss * v[2]]))

    def vee(self) -> V3:
        # w, x, y, z = self
        w, x, y, z = self[0], self[1], self[2], self[3]
        return V3(T2.new_from_heterogeneous_array([x, y, z]))

    def __repr__(self) -> str:
        return f"LieAlgH1(\n{self.array.array}\n)"

    def __str__(self) -> str:
        return f"LieAlgH1(\n{self.array.array}\n)"
