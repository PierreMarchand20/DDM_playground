from itertools import cycle

import gmsh
from matplotlib import pyplot as plt

from ddm_playground.mesh.gmsh import GmshContextManager, GmshOptions
from ddm_playground.mesh.plot import plot_mesh, plot_submesh

dim = 2
nb_partition: int = 4
gmsh_options = GmshOptions(mesh_name="mesh")

with GmshContextManager(gmsh_options) as mesh_generator:
    lc = 0.1  # characteristic length (mesh size)

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

    # Physical names for boundary
    boundaries = gmsh.model.getEntities(dim=dim - 1)
    for i, (_, boundary_tag) in enumerate(boundaries):
        gmsh.model.addPhysicalGroup(dim - 1, [boundary_tag], name=f"boundary_{i}")

    mesh = mesh_generator.generate(dim, nb_partition)

# matplotlib visualization
fig = plt.figure()
ax1 = fig.add_subplot(121)
ax2 = fig.add_subplot(122)
ax1.set_title(f"{dim}D Mesh from GMSH")
ax1.axis("equal")

ax2.set_title("Partitionning")
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
    linewidth=3,
)


plot_submesh(
    ax2,
    mesh,
    dim,
    mesh.partitions_elements[1],
    label="Subdomain 1",
    color="green",
    linewidth=3,
)
ax1.legend()
ax2.legend()
plt.show()
