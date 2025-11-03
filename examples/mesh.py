from itertools import cycle

import gmsh
import matplotlib.pyplot as plt

from ddm_playground.mesh.gmsh import GmshContextManager, GmshOptions
from ddm_playground.mesh.plot import plot_mesh, plot_submesh

dim = 2
nb_partition = 4
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
        gmsh.model.mesh.setSize(gmsh.model.getEntities(0), lc)

    # Physical names for boundary
    boundaries = gmsh.model.getEntities(dim=dim - 1)
    for i, (boundary_dim, boundary_tag) in enumerate(boundaries):
        gmsh.model.addPhysicalGroup(dim - 1, [boundary_tag], name=f"boundary_{i}")

    mesh = mesh_generator.generate(dim, nb_partition)

    # GMSH visualization
    mesh_generator.fltk()

# matplotlib visualization
fig = plt.figure()
ax1 = fig.add_subplot(121, projection="3d") if dim == 3 else fig.add_subplot(121)
ax2 = fig.add_subplot(122, projection="3d") if dim == 3 else fig.add_subplot(122)
ax1.set_title(f"{dim}D Mesh from Gmsh with boundaries")
ax1.axis("equal")

ax2.set_title(f"Partitionning of {dim}D Mesh from Gmsh")
ax2.axis("equal")

plot_mesh(ax1, mesh)
plot_mesh(ax2, mesh)

colors = plt.cm.tab10.colors
color_iter = cycle(colors)
for (
    boundary_name,
    boundary_dim,
    _,
), elements in mesh.physical_group_elements.items():
    plot_submesh(
        ax1,
        mesh,
        boundary_dim,
        elements,
        label=boundary_name,
        color=next(color_iter),
    )

plot_submesh(
    ax2,
    mesh,
    dim,
    mesh.partitions_elements[0],
    label="Subdomain 0",
    color="red",
    linewidth=1 if dim == 3 else 2,
)

if nb_partition > 1:
    plot_submesh(
        ax2,
        mesh,
        dim,
        mesh.partitions_elements[1],
        label="Subdomain 1",
        color="green",
        linewidth=1 if dim == 3 else 2,
    )
ax1.legend()
ax2.legend()
plt.show()
