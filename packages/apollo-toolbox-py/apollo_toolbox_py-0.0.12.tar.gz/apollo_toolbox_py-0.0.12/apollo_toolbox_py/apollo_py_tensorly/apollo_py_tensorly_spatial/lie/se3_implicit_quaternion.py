from apollo_toolbox_py.apollo_py_tensorly.apollo_py_tensorly_linalg.vectors import V3, V6
from apollo_toolbox_py.apollo_py_tensorly.apollo_py_tensorly_spatial.isometries import Isometry3
from apollo_toolbox_py.apollo_py_tensorly.apollo_py_tensorly_spatial.lie.h1 import LieAlgH1, LieGroupH1
from apollo_toolbox_py.apollo_py_tensorly.apollo_py_tensorly_spatial.lie.so3 import LieAlgSO3
from apollo_toolbox_py.apollo_py_tensorly.apollo_py_tensorly_spatial.quaternions import Quaternion, UnitQuaternion
import tensorly as tl
from apollo_toolbox_py.apollo_py.extra_tensorly_backend import ExtraBackend as T2, Device, DType


class LieGroupISE3q(Isometry3):
    @staticmethod
    def get_lie_alg_type() -> type:
        return LieAlgISE3q

    @classmethod
    def from_isometry3(cls, isometry: 'Isometry3') -> 'LieGroupISE3q':
        rotation = isometry.rotation
        translation = isometry.translation
        return cls(rotation, translation)

    @classmethod
    def from_scaled_axis(cls, scaled_axis: V3, translation: V3) -> 'LieGroupISE3q':
        return LieGroupISE3q.from_isometry3(Isometry3(UnitQuaternion.from_scaled_axis(scaled_axis), translation))

    @classmethod
    def from_euler_angles(cls, euler_angles: V3, translation: V3) -> 'LieGroupISE3q':
        return LieGroupISE3q.from_isometry3(Isometry3(UnitQuaternion.from_euler_angles(euler_angles), translation))

    @classmethod
    def identity(cls, device: Device = Device.CPU, dtype: DType = DType.Float64) -> 'LieGroupISE3q':
        return LieGroupISE3q(UnitQuaternion([1, 0, 0, 0], device, dtype), V3([0, 0, 0], device, dtype))

    def group_operator(self, other: 'LieGroupISE3q') -> 'LieGroupISE3q':
        return LieGroupISE3q.from_isometry3(self @ other)

    def ln(self) -> 'LieAlgISE3q':
        a_quat = LieGroupH1(self.rotation.array).ln()
        u = a_quat.vee()
        a_mat: LieAlgSO3 = LieAlgSO3.from_euclidean_space_element(u)
        beta = u.norm()

        if abs(beta) < 0.00001:
            pp = 0.5 - ((beta ** 2.0) / 24.0) + ((beta ** 4.0) / 720.0)
            qq = (1.0 / 6.0) - ((beta ** 2.0) / 120.0) + ((beta ** 4.0) / 5040.0)
        else:
            pp = (1.0 - tl.cos(beta)) / (beta ** 2.0)
            qq = (beta - tl.sin(beta)) / (beta ** 3.0)

        c_mat = tl.eye(3, device=getattr(beta, "device", None), dtype=beta.dtype) + (pp * a_mat.array) + qq * (a_mat.array @ a_mat.array)
        c_inv = T2.inv(c_mat)

        b = V3(c_inv @ self.translation.array)

        return LieAlgISE3q(a_quat, b)

    def inverse(self) -> 'LieGroupISE3q':
        new_rotation = self.rotation.conjugate()
        new_translation = new_rotation.map_point(-self.translation)
        return LieGroupISE3q(new_rotation, new_translation)

    def displacement(self, other: 'LieGroupISE3q') -> 'LieGroupISE3q':
        return self.inverse().group_operator(other)

    def __repr__(self) -> str:
        return f"LieGroupISE3q(\n  rotation: {self.rotation.array.array},\n  ----- \n  translation: {self.translation.array}\n)"

    def __str__(self) -> str:
        return f"LieGroupISE3q(\n  rotation: {self.rotation.array.array},\n  ----- \n  translation: {self.translation.array}\n)"


class LieAlgISE3q:
    def __init__(self, quaternion: Quaternion, vector: V3):
        self.quaternion = quaternion
        self.vector = vector

    @classmethod
    def from_euclidean_space_element(cls, e: V6) -> 'LieAlgISE3q':
        u = V3(T2.new_from_heterogeneous_array([e[0], e[1], e[2]]))
        q = LieAlgH1.from_euclidean_space_element(u)
        v = V3(T2.new_from_heterogeneous_array([e[3], e[4], e[5]]))
        return LieAlgISE3q(q, v)

    def exp(self) -> 'LieGroupISE3q':
        u = LieAlgH1(self.quaternion.array).vee()
        a_mat: LieAlgSO3 = LieAlgSO3.from_euclidean_space_element(u)

        beta = u.norm()

        if tl.abs(beta) < 0.00001:
            pp = 0.5 - ((beta ** 2.0) / 24.0) + ((beta ** 4.0) / 720.0)
            qq = (1.0 / 6.0) - ((beta ** 2.0) / 120.0) + ((beta ** 4.0) / 5040.0)
        else:
            pp = (1.0 - tl.cos(beta)) / (beta ** 2.0)
            qq = (beta - tl.sin(beta)) / (beta ** 3.0)

        c_mat = tl.eye(3, device=getattr(beta, "device", None), dtype=beta.dtype) + pp * a_mat.array + qq * (
                    a_mat.array @ a_mat.array)
        t = V3(c_mat @ self.vector.array)
        q = LieAlgH1(self.quaternion.array).exp()

        return LieGroupISE3q(UnitQuaternion(q.array), t)

    def vee(self) -> 'V6':
        u = LieAlgH1(self.quaternion.array).vee()
        v = self.vector

        return V6(T2.new_from_heterogeneous_array([u[0], u[1], u[2], v[0], v[1], v[2]]))

    def __repr__(self) -> str:
        return f"LieAlgISE3q(\n  quaternion: {self.quaternion.array},\n  ----- \n  vector: {self.vector.array}\n)"

    def __str__(self) -> str:
        return f"LieAlgISE3q(\n  quaternion: {self.quaternion.array},\n  ----- \n  vector: {self.vector.array}\n)"
