import gmsh
import matplotlib.pyplot as plt

from ddm_playground.mesh.gmsh import GmshContextManager, GmshOptions
from ddm_playground.mesh.plot import plot_mesh, plot_mesh_boundary, plot_mesh_partition

dim = 3
nb_partition = 5
gmsh_options = GmshOptions(mesh_name="mesh")

with GmshContextManager(gmsh_options) as mesh_generator:
    lc = 0.1  # characteristic length (mesh size)

    if dim == 1:
        p1 = gmsh.model.geo.addPoint(0, 0, 0, lc)
        p2 = gmsh.model.geo.addPoint(1, 0, 0, lc)
        l1 = gmsh.model.geo.addLine(p1, p2)
        gmsh.model.geo.synchronize()

    elif dim == 2:
        p1 = gmsh.model.geo.addPoint(0, 0, 0, lc)
        p2 = gmsh.model.geo.addPoint(1, 0, 0, lc)
        p3 = gmsh.model.geo.addPoint(1, 1, 0, lc)
        p4 = gmsh.model.geo.addPoint(0, 1, 0, lc)

        l1 = gmsh.model.geo.addLine(p1, p2)
        l2 = gmsh.model.geo.addLine(p2, p3)
        l3 = gmsh.model.geo.addLine(p3, p4)
        l4 = gmsh.model.geo.addLine(p4, p1)
        cl = gmsh.model.geo.addCurveLoop([l1, l2, l3, l4])
        gmsh.model.geo.addPlaneSurface([cl])
        gmsh.model.geo.synchronize()

    elif dim == 3:
        cube = gmsh.model.occ.addBox(0, 0, 0, 1, 1, 1)
        gmsh.model.occ.synchronize()

    # Physical names for boundary
    boundaries = gmsh.model.getEntities(dim=dim - 1)
    for i, (boundary_dim, boundary_tag) in enumerate(boundaries):
        gmsh.model.addPhysicalGroup(dim - 1, [boundary_tag], name=f"boundary_{i}")

    mesh = mesh_generator.generate(dim, nb_partition)

    # GMSH visualization
    mesh_generator.fltk()

# matplotlib visualization
fig = plt.figure()
if dim == 3:
    ax = fig.add_subplot(111, projection="3d")
else:
    ax = fig.add_subplot(111)
ax.set_title(f"{dim}D Mesh from Gmsh")
ax.axis("equal")
plot_mesh(ax, mesh)
if dim == 1 or dim == 2:
    plot_mesh_boundary(ax, mesh)
if nb_partition > 1:
    plot_mesh_partition(ax, mesh, 0)
plt.show()

# Data
nodes = mesh.nodes
elements = mesh.elements
