import bpy
from typing import Tuple

__all__ = ['BlenderSimpleMaterial']


class BlenderSimpleMaterial:
    def __init__(self, name: str = 'Procedural Material', material_type: str = 'Principled BSDF',
                 default_color: Tuple[float, float, float, float] = (0.2, 0.2, 0.2, 1)) -> None:
        """
        Initialize a new ApolloBlenderSimpleMaterial.

        Parameters:
        - name: The name of the material.
        - material_type: The type of the material ('Principled BSDF' or 'Emission').
        - default_color: The default color of the material.
        """
        self.material: bpy.types.Material = bpy.data.materials.new(name=name)
        self.material.use_backface_culling = True
        self.material.blend_method = 'BLEND'
        self.material_type: str = material_type
        self.material.use_nodes = True
        self.material.node_tree.nodes.remove(self.material.node_tree.nodes.get('Principled BSDF'))

        material_output_node: bpy.types.Node = self.material.node_tree.nodes.get('Material Output')

        if material_type == 'Principled BSDF':
            self.input_node: bpy.types.Node = self.material.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
        elif material_type == 'Emission':
            self.input_node: bpy.types.Node = self.material.node_tree.nodes.new('ShaderNodeEmission')
            self.input_node.inputs['Strength'].default_value = 0.5

        self.material.node_tree.links.new(material_output_node.inputs[0], self.input_node.outputs[0])

        self.default_color: Tuple[float, float, float, float] = default_color

        self.input_node.inputs[0].default_value = default_color

    @classmethod
    def from_already_existing_material(cls, material: bpy.types.Material, material_type: str = 'Principled BSDF',
                                       default_color: Tuple[float, float, float, float] = (0.2, 0.2, 0.2, 1)):
        """
        Create a BlenderSimpleMaterial from an existing Blender material.

        Parameters:
        - material: The existing Blender material.
        - material_type: The type of the material ('Principled BSDF' or 'Emission').
        - default_color: The default color of the material.
        """
        if not material.use_nodes:
            raise ValueError("The existing material must use nodes.")

        instance = cls(name=material.name, material_type=material_type, default_color=default_color)
        instance.material = material
        instance.material_type = material_type

        material_output_node = material.node_tree.nodes.get('Material Output')
        if not material_output_node:
            raise ValueError("The existing material must have a 'Material Output' node.")

        input_node = None
        for node in material.node_tree.nodes:
            if (material_type == 'Principled BSDF' and node.type == 'BSDF_PRINCIPLED') or \
               (material_type == 'Emission' and node.type == 'EMISSION'):
                input_node = node
                break

        if not input_node:
            raise ValueError(f"No '{material_type}' node found in the existing material.")

        instance.input_node = input_node
        instance.default_color = default_color

        input_node.inputs[0].default_value = default_color

        return instance

    def apply_material_to_object(self, blender_object: bpy.types.Object):
        """
        Apply this material to a Blender object.

        Parameters:
        - object: The Blender object to which the material is applied.
        """
        blender_object.active_material = self.material

    def set_color(self, color: Tuple[float, float, float, float]):
        """
        Set the color of the material.

        Parameters:
        - color: The new color of the material.
        """
        self.input_node.inputs[0].default_value = color

    def set_alpha(self, alpha: float):
        """
        Set the alpha (transparency) of the material.

        Parameters:
        - alpha: The new alpha value of the material.
        """
        if self.material_type == 'Principled BSDF':
            # print(self.input_node.inputs[21])
            # self.input_node.inputs[21].default_value = alpha
            self.input_node.inputs['Alpha'].default_value = alpha

    def reset_color(self):
        """
        Reset the color of the material to the default color.
        """
        self.input_node.inputs[0].default_value = self.default_color

    def keyframe_material(self, frame: int):
        """
        Insert keyframes for the material properties at the specified frame.

        Parameters:
        - frame: The frame number at which to insert keyframes.
        """
        if self.material_type == 'Principled BSDF':
            self.input_node.inputs[0].keyframe_insert('default_value', frame=frame)  # color
            self.input_node.inputs['Alpha'].keyframe_insert('default_value', frame=frame)  # alpha
        if self.material_type == 'Emission':
            self.input_node.inputs[0].keyframe_insert('default_value', frame=frame)
            self.input_node.inputs['Strength'].keyframe_insert('default_value', frame=frame)
