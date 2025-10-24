import logging

import matplotlib.pyplot as plt
import matplotlib.tri as mtri
import numpy as np

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
        "marker": "o",
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


def plot_submesh(ax, mesh, dim, elements, **kwargs):
    """
    Plot the submesh.

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

    if 0 < mesh.dim < 3 and 0 <= dim < 3 and dim <= mesh.dim:
        if dim == 0:
            for e in elements:
                x, y, _ = mesh.nodes[e, 0], mesh.nodes[e, 1], mesh.nodes[e, 2]
                ax.plot(x, y, **style)

        elif dim == 1:
            for e in elements:
                x, y, _ = mesh.nodes[e, 0], mesh.nodes[e, 1], mesh.nodes[e, 2]
                ax.plot(
                    x,
                    y,
                    **style,
                )
                style["label"] = None
        elif dim == 2:
            x = mesh.nodes[:, 0]
            y = mesh.nodes[:, 1]
            triang = mtri.Triangulation(x, y, elements)
            ax.triplot(triang, **style)
    elif mesh.dim == 3 and 2 <= dim <= 3:
        for tet in elements:
            verts = mesh.nodes[tet]
            if dim == 2:
                edges = [
                    [verts[0], verts[1]],
                    [verts[0], verts[2]],
                    [verts[1], verts[2]],
                ]
            elif dim == 3:
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
                style["label"] = None
    else:
        raise ValueError(
            f"Unsupported mesh dimension {mesh.dim} with submesh dimension {dim}"
        )

    # ax.legend()
