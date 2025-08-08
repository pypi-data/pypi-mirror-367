from apollo_toolbox_py.apollo_py_blender.robotics.chain_blender import ChainBlender
from apollo_toolbox_py.prelude import *

r = ResourcesRootDirectory.new_from_default_apollo_robots_dir()
s = r.get_subdirectory('ur5')
c = s.to_chain_tensorly()

cc = ChainBlender.spawn(c, r)

cc2 = ChainBlender.capture_already_existing_chain(0, c, r)

cc2.set_link_plain_mesh_color(2, (1.0, 0., 0., 1.0))
