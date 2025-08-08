from typing import Optional, Dict, List, Union, Type

from apollo_toolbox_py.apollo_py.apollo_py_robotics.robot_preprocessed_modules.urdf_module import ApolloURDFMimic, \
    ApolloURDFLimit, ApolloURDFSafetyController, ApolloURDFDynamics, ApolloURDFJoint, ApolloURDFMaterial, \
    ApolloURDFModule, ApolloURDFGeometry, ApolloURDFVisual, ApolloURDFCollision, ApolloURDFLink, ApolloURDFPose, \
    ApolloURDFInertia, ApolloURDFMass, ApolloURDFInertial, ApolloURDFAxis
from apollo_toolbox_py.apollo_py.extra_tensorly_backend import Device, DType
from apollo_toolbox_py.apollo_py_tensorly.apollo_py_tensorly_linalg.matrices import M, M3
from apollo_toolbox_py.apollo_py_tensorly.apollo_py_tensorly_linalg.vectors import V3
from apollo_toolbox_py.apollo_py_tensorly.apollo_py_tensorly_spatial.lie.se3_implicit import LieGroupISE3
from apollo_toolbox_py.apollo_py_tensorly.apollo_py_tensorly_spatial.lie.se3_implicit_quaternion import LieGroupISE3q
from apollo_toolbox_py.apollo_py_tensorly.apollo_py_tensorly_spatial.quaternions import UnitQuaternion
from apollo_toolbox_py.apollo_py_tensorly.apollo_py_tensorly_spatial.rotation_matrices import Rotation3


class ApolloURDFTensorlyPose:
    def __init__(self, xyz: V3, rpy: V3):
        self.xyz = xyz
        self.rpy = rpy
        self.pose: LieGroupISE3q = LieGroupISE3q(UnitQuaternion.from_euler_angles(rpy), xyz)
        self.pose_m: LieGroupISE3 = LieGroupISE3(Rotation3.from_euler_angles(rpy), xyz)

    @classmethod
    def from_apollo_urdf_pose(cls, pose: ApolloURDFPose, device: Device, dtype: DType):
        return cls(V3(pose.xyz, device, dtype), V3(pose.rpy, device, dtype))

    def get_pose_from_lie_group_type(self, lie_group_type: Union[Type[LieGroupISE3q], Type[LieGroupISE3]]) -> Union[LieGroupISE3q, LieGroupISE3]:
        if issubclass(lie_group_type, LieGroupISE3):
            return self.pose_m
        elif issubclass(lie_group_type, LieGroupISE3q):
            return self.pose
        else:
            raise ValueError('not legal argument')

    def __repr__(self):
        return f"ApolloURDFTensorlyPose(xyz={self.xyz}, rpy={self.rpy})"


class ApolloURDFTensorlyInertia:
    def __init__(self, inertia_matrix: M3):
        self.inertia_matrix = inertia_matrix

    @classmethod
    def from_apollo_urdf_inertia(cls, inertia: ApolloURDFInertia, device: Device, dtype: DType):
        inertia_matrix = M3([
            [inertia.ixx, inertia.ixy, inertia.ixz],
            [inertia.ixy, inertia.iyy, inertia.iyz],
            [inertia.ixz, inertia.iyz, inertia.izz]
        ], device, dtype)
        return cls(inertia_matrix)

    def __repr__(self):
        return f"ApolloURDFTensorlyInertia(inertia_matrix={self.inertia_matrix})"


class ApolloURDFTensorlyInertial:
    def __init__(self, origin: ApolloURDFTensorlyPose, mass: ApolloURDFMass, inertia: ApolloURDFTensorlyInertia):
        self.origin = origin
        self.mass = mass
        self.inertia = inertia

    @classmethod
    def from_apollo_urdf_inertial(cls, inertial: ApolloURDFInertial, device: Device, dtype: DType):
        origin = ApolloURDFTensorlyPose.from_apollo_urdf_pose(inertial.origin, device, dtype)
        inertia = ApolloURDFTensorlyInertia.from_apollo_urdf_inertia(inertial.inertia, device, dtype)
        return cls(origin, inertial.mass, inertia)

    def __repr__(self):
        return (f"ApolloURDFTensorlyInertial(origin={self.origin}, mass={self.mass}, "
                f"inertia={self.inertia})")


class ApolloURDFTensorlyAxis:
    def __init__(self, xyz: V3):
        self.xyz: V3 = xyz

    @classmethod
    def from_apollo_urdf_axis(cls, axis: ApolloURDFAxis, device: Device, dtype: DType):
        return cls(V3(axis.xyz, device, dtype))

    def __repr__(self):
        return f"ApolloURDFTensorlyAxis(xyz={self.xyz})"


class ApolloURDFTensorlyVisual:
    def __init__(self, name: Optional[str], origin: ApolloURDFTensorlyPose, geometry: ApolloURDFGeometry,
                 material: Optional[ApolloURDFMaterial]):
        self.name = name
        self.origin = origin
        self.geometry = geometry
        self.material = material

    @classmethod
    def from_apollo_urdf_visual(cls, visual: ApolloURDFVisual, device: Device, dtype: DType):
        origin = ApolloURDFTensorlyPose.from_apollo_urdf_pose(visual.origin, device, dtype)
        return cls(visual.name, origin, visual.geometry, visual.material)

    def __repr__(self):
        return (f"ApolloURDFTensorlyVisual(name={self.name}, origin={self.origin}, "
                f"geometry={self.geometry}, material={self.material})")


class ApolloURDFTensorlyCollision:
    def __init__(self, name: Optional[str], origin: ApolloURDFTensorlyPose, geometry: ApolloURDFGeometry):
        self.name = name
        self.origin = origin
        self.geometry = geometry

    @classmethod
    def from_apollo_urdf_collision(cls, collision: ApolloURDFCollision, device: Device, dtype: DType):
        origin = ApolloURDFTensorlyPose.from_apollo_urdf_pose(collision.origin, device, dtype)
        return cls(collision.name, origin, collision.geometry)

    def __repr__(self):
        return (f"ApolloURDFTensorlyCollision(name={self.name}, origin={self.origin}, "
                f"geometry={self.geometry})")


class ApolloURDFTensorlyLink:
    def __init__(self, name: str, inertial: ApolloURDFTensorlyInertial, visual: List[ApolloURDFTensorlyVisual],
                 collision: List[ApolloURDFTensorlyCollision]):
        self.name = name
        self.inertial = inertial
        self.visual = visual
        self.collision = collision

    @classmethod
    def from_apollo_urdf_link(cls, link: ApolloURDFLink, device: Device, dtype: DType):
        inertial = ApolloURDFTensorlyInertial.from_apollo_urdf_inertial(link.inertial, device, dtype)
        visual = [ApolloURDFTensorlyVisual.from_apollo_urdf_visual(v, device, dtype) for v in link.visual]
        collision = [ApolloURDFTensorlyCollision.from_apollo_urdf_collision(c, device, dtype) for c in link.collision]
        return cls(link.name, inertial, visual, collision)

    def __repr__(self):
        return (f"ApolloURDFTensorlyLink(name={self.name}, inertial={self.inertial}, "
                f"visual={self.visual}, collision={self.collision})")


class ApolloURDFTensorlyJoint:
    def __init__(self, name: str, joint_type: str, origin: ApolloURDFTensorlyPose, parent: Dict[str, str],
                 child: Dict[str, str],
                 axis: ApolloURDFTensorlyAxis, limit: ApolloURDFLimit, dynamics: Optional[ApolloURDFDynamics] = None,
                 mimic: Optional[ApolloURDFMimic] = None,
                 safety_controller: Optional[ApolloURDFSafetyController] = None):
        self.name = name
        self.joint_type = joint_type
        self.origin = origin
        self.parent = parent
        self.child = child
        self.axis = axis
        self.limit = limit
        self.dynamics = dynamics
        self.mimic = mimic
        self.safety_controller = safety_controller

    @classmethod
    def from_apollo_urdf_joint(cls, joint: ApolloURDFJoint, device: Device, dtype: DType):
        origin = ApolloURDFTensorlyPose.from_apollo_urdf_pose(joint.origin, device, dtype)
        axis = ApolloURDFTensorlyAxis.from_apollo_urdf_axis(joint.axis, device, dtype)
        return cls(joint.name, joint.joint_type, origin, joint.parent, joint.child, axis, joint.limit, joint.dynamics,
                   joint.mimic, joint.safety_controller)

    def __repr__(self):
        return (f"ApolloURDFTensorlyJoint(name={self.name}, joint_type={self.joint_type}, "
                f"origin={self.origin}, parent={self.parent}, child={self.child}, "
                f"axis={self.axis}, limit={self.limit}, dynamics={self.dynamics}, "
                f"mimic={self.mimic}, safety_controller={self.safety_controller})")


class ApolloURDFTensorlyModule:
    def __init__(self, name: str, links: List[ApolloURDFTensorlyLink], joints: List[ApolloURDFTensorlyJoint],
                 materials: List[ApolloURDFMaterial]):
        self.name = name
        self.links = links
        self.joints = joints
        self.materials = materials

    @classmethod
    def from_urdf_module(cls, urdf_module: ApolloURDFModule, device: Device = Device.CPU, dtype: DType = DType.Float64):
        links = [ApolloURDFTensorlyLink.from_apollo_urdf_link(link, device, dtype) for link in urdf_module.links]
        joints = [ApolloURDFTensorlyJoint.from_apollo_urdf_joint(joint, device, dtype) for joint in urdf_module.joints]
        return cls(urdf_module.name, links, joints, urdf_module.materials)

    def __repr__(self):
        return (f"ApolloURDFTensorlyModule(name={self.name}, links={self.links}, "
                f"joints={self.joints}, materials={self.materials})")