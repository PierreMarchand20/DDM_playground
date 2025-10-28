import gmsh

from ddm_playground.mesh.gmsh import GmshContextManager, GmshOptions

dim: int = 2
nb_partition: int = 4
gmsh_options = GmshOptions(mesh_name="mesh")

with GmshContextManager(gmsh_options) as mesh_generator:
    lc = 0.1  # characteristic length (mesh size)

    p1 = gmsh.model.geo.addPoint(0, 0, 0, lc)
    p2 = gmsh.model.geo.addPoint(1, 0, 0, lc)
    l1 = gmsh.model.geo.addLine(p1, p2)
    gmsh.model.geo.synchronize()
    mesh = mesh_generator.generate(dim, nb_partition)
