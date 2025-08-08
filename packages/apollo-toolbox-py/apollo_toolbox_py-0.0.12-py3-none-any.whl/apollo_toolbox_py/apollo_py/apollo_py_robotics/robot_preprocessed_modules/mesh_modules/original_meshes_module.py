from typing import List, Optional, Dict

from apollo_toolbox_py.apollo_py.apollo_py_robotics.robot_preprocessed_modules.mesh_modules.utils import \
    recover_full_mesh_path_bufs_from_relative_mesh_paths_options
from apollo_toolbox_py.apollo_py.path_buf import PathBuf


# from apollo_toolbox_py.apollo_py.path_buf import PathBufPyWrapper


class ApolloOriginalMeshesModule:
    def __init__(self, link_mesh_relative_paths: List[List[str]]):
        # Each inner list of strings → inner list of PathBufs
        self.link_mesh_relative_paths: List[List[PathBuf]] = [
            [PathBuf().append(p) for p in paths]
            for paths in link_mesh_relative_paths
        ]

    def __repr__(self):
        # Show nested lists of strings
        nested = [
            [p.to_string() for p in paths]
            for paths in self.link_mesh_relative_paths
        ]
        return f"ApolloOriginalMeshesModule(link_mesh_relative_paths={nested})"

    def recover_full_path_bufs(self, resources_root_directory) -> List[List[PathBuf]]:
        # Recover each sublist separately
        return [
            recover_full_mesh_path_bufs_from_relative_mesh_paths_options(
                resources_root_directory,
                paths
            )
            for paths in self.link_mesh_relative_paths
        ]

    @classmethod
    def from_dict(cls, data: Dict) -> 'ApolloOriginalMeshesModule':
        # data['link_mesh_relative_paths'] should now be List[List[str]]
        return cls(data['link_mesh_relative_paths'])
