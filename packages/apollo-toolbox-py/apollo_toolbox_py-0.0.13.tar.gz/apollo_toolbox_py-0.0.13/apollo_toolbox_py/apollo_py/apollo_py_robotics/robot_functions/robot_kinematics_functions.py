__all__ = ['RobotKinematicFunctions']

from typing import Union, TypeVar, Type, List

from apollo_toolbox_py.apollo_py.apollo_py_robotics.robot_preprocessed_modules.chain_module import ApolloChainModule
from apollo_toolbox_py.apollo_py.apollo_py_robotics.robot_preprocessed_modules.dof_module import ApolloDOFModule
from apollo_toolbox_py.apollo_py.extra_tensorly_backend import Device, DType
from apollo_toolbox_py.apollo_py_numpy.apollo_py_numpy_linalg.vectors import V3 as V3Numpy, V6 as V6Numpy, V as VNumpy
from apollo_toolbox_py.apollo_py_tensorly.apollo_py_tensorly_linalg.vectors import V3 as V3Tensorly, V6 as V6Tensorly, \
    V as VTensorly
from apollo_toolbox_py.apollo_py_numpy.apollo_py_numpy_robotics.robot_runtime_modules.urdf_numpy_module import \
    ApolloURDFNumpyModule
from apollo_toolbox_py.apollo_py_numpy.apollo_py_numpy_spatial.lie.se3_implicit import LieGroupISE3 as LieGroupISE3Numpy
from apollo_toolbox_py.apollo_py_numpy.apollo_py_numpy_spatial.lie.se3_implicit_quaternion import \
    LieGroupISE3q as LieGroupISE3qNumpy
from apollo_toolbox_py.apollo_py_tensorly.apollo_py_tensorly_spatial.lie.se3_implicit import \
    LieGroupISE3 as LieGroupISE3Tensorly
from apollo_toolbox_py.apollo_py_tensorly.apollo_py_tensorly_spatial.lie.se3_implicit_quaternion import \
    LieGroupISE3q as LieGroupISE3qTensorly
from apollo_toolbox_py.apollo_py_tensorly.apollo_py_tensorly_robotics.robot_runtime_modules.urdf_tensorly_module import \
    ApolloURDFTensorlyModule

U = TypeVar('U', bound=Union[ApolloURDFNumpyModule, ApolloURDFTensorlyModule])
LT = TypeVar('LT', bound=Union[
    Type[LieGroupISE3qNumpy], Type[LieGroupISE3Numpy], Type[LieGroupISE3qTensorly], Type[LieGroupISE3Tensorly]])
L = TypeVar('L', bound=Union[LieGroupISE3qNumpy, LieGroupISE3Numpy, LieGroupISE3qTensorly, LieGroupISE3Tensorly])
V3 = TypeVar('V3', bound=Union[V3Numpy, V3Tensorly])
V3T = TypeVar('V3T', bound=Union[Type[V3Numpy], Type[V3Tensorly]])
V6 = TypeVar('V6', bound=Union[V6Numpy, V6Tensorly])
V = TypeVar('V', bound=Union[VNumpy, VTensorly])
VT = TypeVar('VT', bound=Union[Type[VNumpy], Type[VTensorly]])


class RobotKinematicFunctions:
    @staticmethod
    def fk(state: V, urdf_module: U, chain_module: ApolloChainModule, dof_module: ApolloDOFModule,
           lie_group_type: LT, vector3_type: V3, vector6_type: V6, device: Device = Device.CPU, dtype: DType = DType.Float64) -> List[L]:
        assert len(state.array) == dof_module.num_dofs

        links = urdf_module.links
        joints = urdf_module.joints
        kinematic_hierarchy = chain_module.kinematic_hierarchy
        joint_idx_to_dofs_mapping = dof_module.joint_idx_to_dof_idxs_mapping

        num_links = len(links)
        out = [lie_group_type.identity(device, dtype) for _ in range(num_links)]

        for i, layer in enumerate(kinematic_hierarchy):
            if i == 0:
                continue

            for link_idx in layer:
                link_in_chain = chain_module.links_in_chain[link_idx]
                parent_link_idx = link_in_chain.parent_link_idx
                parent_joint_idx = link_in_chain.parent_joint_idx
                parent_joint = joints[parent_joint_idx]
                constant_transform = parent_joint.origin.get_pose_from_lie_group_type(lie_group_type)

                if parent_joint.mimic:
                    mimic_joint_name = parent_joint.mimic.joint
                    mimic_joint_in_chain = next(x for x in chain_module.joints_in_chain if x.joint_name == mimic_joint_name)
                    dof_idxs = joint_idx_to_dofs_mapping[mimic_joint_in_chain.joint_idx]
                    joint_dofs = [
                        (parent_joint.mimic.offset if parent_joint.mimic.offset is not None else 0.0)
                        + (parent_joint.mimic.multiplier if parent_joint.mimic.multiplier is not None else 1.0) * state[i]
                        for i in dof_idxs
                    ]
                else:
                    dof_idxs = joint_idx_to_dofs_mapping[parent_joint_idx]
                    joint_dofs = [state[i] for i in dof_idxs]

                joint_axis = parent_joint.axis.xyz
                joint_type = parent_joint.joint_type
                variable_transform = RobotKinematicFunctions.get_joint_variable_transform(joint_type, joint_axis,
                                                                                          joint_dofs, lie_group_type,
                                                                                          vector3_type, vector6_type,
                                                                                          device, dtype)

                out[link_idx] = out[parent_link_idx].group_operator(constant_transform).group_operator \
                    (variable_transform)

        return out

    @staticmethod
    def reverse_of_fk(link_frames: List[L], urdf_module: U, chain_module: ApolloChainModule,
                      dof_module: ApolloDOFModule,
                      lie_group_type: LT, vec_type: VT, vector3_type: V3, device: Device = Device.CPU, dtype: DType = DType.Float64) -> V:
        out = vec_type(dof_module.num_dofs * [0.0], device, dtype)

        for joint_in_chain in chain_module.joints_in_chain:
            joint_idx = joint_in_chain.joint_idx
            parent_link_idx = joint_in_chain.parent_link_idx
            child_link_idx = joint_in_chain.child_link_idx
            joint = urdf_module.joints[joint_idx]
            constant_transform = joint.origin.get_pose_from_lie_group_type(lie_group_type)
            joint_type = joint.joint_type
            dof_idxs = dof_module.joint_idx_to_dof_idxs_mapping[joint_idx]
            axis = joint.axis.xyz

            t_variable = constant_transform.inverse().group_operator(
                link_frames[parent_link_idx].inverse()).group_operator(link_frames[child_link_idx])
            t_variable_vee = t_variable.ln().vee()

            if joint_type == 'Revolute' or joint_type == 'Continuous':
                value = t_variable_vee.norm()
                tmp = vector3_type([t_variable_vee[0], t_variable_vee[1], t_variable_vee[2]])
                d = axis.dot(tmp)
                if issubclass(lie_group_type, LieGroupISE3qTensorly) or issubclass(lie_group_type, LieGroupISE3qNumpy):
                    value *= 2.0
                if d < 0.0:
                    value = -value
                out[dof_idxs[0]] = value
            elif joint_type == 'Prismatic':
                value = t_variable_vee.norm()
                tmp = vector3_type([t_variable_vee[3], t_variable_vee[4], t_variable_vee[5]])
                d = axis.dot(tmp)
                if d < 0.0:
                    value = -value
                out[dof_idxs[0]] = value
            elif joint_type == 'Floating':
                for i, x in enumerate(dof_idxs):
                    out[x] = t_variable_vee[i]
            elif joint_type == 'Planar':
                out[dof_idxs[0]] = t_variable_vee[4]
                out[dof_idxs[1]] = t_variable_vee[5]
            elif joint_type == 'Spherical':
                out[dof_idxs[0]] = t_variable_vee[0]
                out[dof_idxs[1]] = t_variable_vee[1]
                out[dof_idxs[2]] = t_variable_vee[2]

        return out

    @staticmethod
    def get_joint_variable_transform(joint_type: str, joint_axis, joint_dofs, lie_group_type: LT, vector3_type: V3,
                                     vector6_type: V6, device: Device = Device.CPU, dtype: DType = DType.Float64):
        if joint_type == 'Revolute':
            assert len(joint_dofs) == 1
            sa = joint_dofs[0] * joint_axis
            return lie_group_type.from_scaled_axis(sa, vector3_type([0, 0, 0], device, dtype))
        elif joint_type == 'Continuous':
            assert len(joint_dofs) == 1
            sa = joint_dofs[0] * joint_axis
            return lie_group_type.from_scaled_axis(sa, vector3_type([0, 0, 0], device, dtype))
        elif joint_type == 'Prismatic':
            assert len(joint_dofs) == 1
            sa = joint_dofs[0] * joint_axis
            return lie_group_type.from_scaled_axis(vector3_type([0, 0, 0], device, dtype), sa)
        elif joint_type == 'Fixed':
            assert len(joint_dofs) == 0
            return lie_group_type.identity(device, dtype)
        elif joint_type == 'Floating':
            assert len(joint_dofs) == 6
            v6 = vector6_type(joint_dofs)
            return lie_group_type.get_lie_alg_type().from_euclidean_space_element(v6).exp()
        elif joint_type == 'Planar':
            assert len(joint_dofs) == 2
            t = vector3_type([joint_dofs[0], joint_dofs[1], 0.0])
            return lie_group_type.from_scaled_axis(vector3_type([0, 0, 0], device, dtype), t)
        elif joint_type == 'Spherical':
            assert len(joint_dofs) == 3
            v = vector3_type(joint_dofs)
            return lie_group_type.from_scaled_axis(v, vector3_type([0, 0, 0], device, dtype))
        else:
            raise ValueError(f"not valid joint type: {joint_type}")
