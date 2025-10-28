import logging
from itertools import cycle

import matplotlib.pyplot as plt

import gmsh
from ddm_playground.mesh.gmsh import GmshContextManager, GmshOptions
from ddm_playground.mesh.overlap import add_overlap
from ddm_playground.mesh.plot import plot_mesh, plot_submesh

logging.getLogger().setLevel(logging.INFO)

dim = 2
nb_partition = 3
additional_overlap = 1
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

submeshes, neighbors, intersections, _ = add_overlap(mesh, additional_overlap)

# matplotlib visualization
ncols = 2
nrow = 2 if nb_partition > 2 else 1
fig = plt.figure()
x = mesh.nodes[:, 0]
y = mesh.nodes[:, 1]
z = mesh.nodes[:, 2]

colors = plt.cm.tab10.colors

for partition_index in range(min(nb_partition, 4)):
    color_iter = cycle(colors)
    ax = (
        fig.add_subplot(nrow, ncols, partition_index + 1, projection="3d")
        if dim == 3
        else fig.add_subplot(nrow, ncols, partition_index + 1)
    )
    plot_mesh(ax, mesh)

    # Partition
    plot_submesh(
        ax,
        mesh,
        dim,
        mesh.partitions_elements[partition_index],
        color=next(color_iter),
        label=f"Partition {partition_index}",
        # linestyle="none",
        markersize=5,
    )

    # Subdomain with overlap
    plot_mesh(
        ax,
        submeshes[partition_index],
        linestyle="none",
        label=f"Nodes in subdomain {partition_index}",
        color=next(color_iter),
        marker="x",
        markersize=10,
    )

    # Physical boundary of subdomain
    for (
        boundary_name,
        boundary_dim,
        _,
    ), elements in submeshes[partition_index].physical_group_elements.items():
        plot_submesh(
            ax,
            submeshes[partition_index],
            boundary_dim,
            elements,
            label=boundary_name,
            color=next(color_iter),
        )
    ax.legend()
    ax.set_title(f"Subdomain {partition_index}")
    ax.axis("equal")
plt.show()
