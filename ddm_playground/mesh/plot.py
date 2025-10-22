import logging

import matplotlib.pyplot as plt
import matplotlib.tri as mtri

logger = logging.getLogger(__name__)


def plot_mesh(ax, mesh, **kwargs):
    """
    Plot the mesh.

    Parameters:
        ax : matplotlib Axes object
        **kwargs : styling options (color, linewidth, marker, etc.)
    """

    default_style = {
        "color": "black",
        "linewidth": 0.8,
        "marker": "o" if mesh.dim == 1 else None,
        "markersize": 3,
    }
    style = {**default_style, **kwargs}

    x = mesh.nodes[:, 0]
    y = mesh.nodes[:, 1]
    if mesh.dim == 1:
        ax.plot(x, y, **style)

    elif mesh.dim == 2:
        triang = mtri.Triangulation(x, y, mesh.elements)
        ax.triplot(triang, **style)

    elif mesh.dim == 3:
        ax.scatter(
            mesh.nodes[:, 0], mesh.nodes[:, 1], mesh.nodes[:, 2], color="k", s=10
        )
        for tet in mesh.elements:
            verts = mesh.nodes[tet]
            edges = [
                [verts[0], verts[1]],
                [verts[0], verts[2]],
                [verts[0], verts[3]],
                [verts[1], verts[2]],
                [verts[1], verts[3]],
                [verts[2], verts[3]],
            ]
            for e in edges:
                ax.plot(*zip(*e), color="b", linewidth=0.5)

        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        ax.set_box_aspect([1, 1, 1])


def plot_mesh_boundary(ax, mesh, **kwargs):
    """
    Plot the mesh boundary.

    Parameters:
        ax : matplotlib Axes object
        **kwargs : styling options (color, linewidth, marker, etc.)
    """

    default_style = {
        "linewidth": 2,
        "marker": "o" if mesh.dim == 1 else None,
        "markersize": 3,
    }
    style = {**default_style, **kwargs}

    colors = plt.cm.tab10.colors
    for i, (name, elems) in enumerate(mesh.boundary_elements.items()):
        color = colors[i % len(colors)]
        if mesh.dim == 1:
            for e in elems:
                # print(e)
                x, y, _ = mesh.nodes[e, 0], mesh.nodes[e, 1], mesh.nodes[e, 2]
                ax.plot(x, y, label=name, color=color, **style)

        elif mesh.dim == 2:
            # Boundary is 1D lines
            label_done = False
            for e in elems:
                x, y, _ = mesh.nodes[e, 0], mesh.nodes[e, 1], mesh.nodes[e, 2]
                ax.plot(
                    x,
                    y,
                    color=color,
                    label=name if not label_done else None,
                    linewidth=2,
                )
                label_done = True
        # elif dim == 3:
        #     # Boundary is 2D triangles
        #     for e in elems:
        #         verts = mesh.nodes[e]
        #         tri = Poly3DCollection(
        #             [verts], facecolor=color, edgecolor="k", alpha=0.5
        #         )
        #         ax.add_collection3d(tri)
        else:
            raise ValueError(f"Unsupported dimension {mesh.dim}")

        ax.legend()


def plot_mesh_partition(ax, mesh, partition_id, **kwargs):
    """
    Plot the mesh partition numbered "partition_id".

    Parameters:
        ax : matplotlib Axes object
        partition_id : partition number to be plotted
        **kwargs : styling options (color, linewidth, marker, etc.)
    """

    default_style = {
        "color": "red",
        "linewidth": 1.5,
        "marker": "o" if mesh.dim == 1 else None,
        "markersize": 3,
    }
    style = {**default_style, **kwargs}
    x = mesh.nodes[:, 0]
    y = mesh.nodes[:, 1]
    z = mesh.nodes[:, 2]
    if mesh.dim == 1:
        print(mesh.partition_elements[partition_id])
        for e in mesh.partition_elements[partition_id]:
            ax.plot(x[e], y[e], **style)

    elif mesh.dim == 2:
        triang = mtri.Triangulation(x, y, mesh.partition_elements[partition_id])
        ax.triplot(triang, **style)

    elif mesh.dim == 3:
        for tet in mesh.partition_elements[partition_id]:
            verts = mesh.nodes[tet]
            # ax.scatter(x[tet], y[tet], z[tet], color="r")
            edges = [
                [verts[0], verts[1]],
                [verts[0], verts[2]],
                [verts[0], verts[3]],
                [verts[1], verts[2]],
                [verts[1], verts[3]],
                [verts[2], verts[3]],
            ]
            for e in edges:
                ax.plot(*zip(*e), **style)

        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        ax.set_box_aspect([1, 1, 1])
    else:
        raise ValueError(f"Unsupported dimension {mesh.dim}")
