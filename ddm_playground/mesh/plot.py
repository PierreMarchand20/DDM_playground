import copy
import logging

import matplotlib.tri as mtri
from matplotlib.axes import Axes
from mpl_toolkits.mplot3d import Axes3D

from ddm_playground.mesh.data import MeshData

logger = logging.getLogger(__name__)


def plot_mesh(ax: Axes | Axes3D, mesh: MeshData, **kwargs) -> None:
    """
    Plot a finite element mesh in 1D, 2D, or 3D.

    This function provides a simple, dimension-aware visualization
    for meshes represented by a :class:`MeshData` object. It supports
    plotting nodes and element edges for 1D, 2D (triangular), and
    3D (tetrahedral) meshes.

    Parameters
    ----------
    ax : matplotlib.axes.Axes or mpl_toolkits.mplot3d.Axes3D
        The matplotlib Axes on which to plot the mesh.
        - For 1D and 2D, use a standard 2D Axes.
        - For 3D meshes, use a 3D Axes (`projection='3d'`).

    mesh : MeshData
        The mesh to plot. Must contain:
          - ``mesh.nodes``: array of node coordinates, shape (N, dim)
          - ``mesh.elements``: array of element connectivity, shape (M, n_nodes_per_elem)
          - ``mesh.dim``: spatial dimension (1, 2, or 3)

    **kwargs : dict, optional
        Additional matplotlib style arguments such as:
        - ``color``: edge or marker color (default: black)
        - ``linewidth``: width of element edges (default: 0.8)
        - ``marker``: node marker style (default: 'o')
        - ``markersize``: node marker size (default: 3)
        - ``label``: label for legend (optional)

    Notes
    -----
    * In 2D, this function uses :class:`matplotlib.tri.Triangulation` internally
      to plot triangular meshes.
    * In 3D, only the mesh edges of tetrahedra are plotted for clarity.
    * The function does not return anything; it draws directly on the given Axes.

    Raises
    ------
    ValueError
        If `dim` is incompatible with the mesh dimension.
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

        style_without_label = copy.deepcopy(style)
        style_without_label.pop("label", None)
        ax.triplot(triang, **style_without_label)

        style_without_line = copy.deepcopy(style)
        style_without_line["linestyle"] = "none"
        ax.plot(triang.x, triang.y, **style_without_line)

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
    else:
        raise ValueError(f"Unsupported mesh dimension: {mesh.dim}")


def plot_submesh(
    ax: Axes | Axes3D,
    mesh: MeshData,
    dim: int,
    elements: list[list[int]],
    **kwargs,
) -> None:
    """
    Plot a submesh of a finite element mesh.

    This function allows plotting a subset of elements from a MeshData object,
    supporting 1D, 2D, and 3D meshes. The subset can be lower-dimensional
    (e.g., edges of a tetrahedron or faces of a triangle) for visualization
    of boundaries, interfaces, or specific element groups.

    Parameters
    ----------
    ax : matplotlib.axes.Axes or mpl_toolkits.mplot3d.Axes3D
        The matplotlib Axes to plot on.
        - Use a standard 2D Axes for 1D/2D meshes.
        - Use a 3D Axes (`projection='3d'`) for 3D meshes.

    mesh : MeshData
        The mesh containing node coordinates and element connectivity.

    dim : int
        Topological dimension of the submesh to plot:
        - 0: nodes
        - 1: edges (1D elements or edges of higher-dimensional elements)
        - 2: faces (triangles in 3D)
        - 3: tetrahedra (3D volume elements)

    elements : list of list of int
        List of elements to plot. Each element is a list of node indices
        defining the connectivity.

    **kwargs : dict, optional
        Additional matplotlib style arguments (color, linewidth, marker, etc.).

    Notes
    -----
    * For 2D meshes, the function uses :class:`matplotlib.tri.Triangulation`.
    * For 3D meshes, edges of faces or tetrahedra are plotted manually.
    * Labels are removed for individual elements to avoid duplicate legend entries.

    Raises
    ------
    ValueError
        If `dim` is incompatible with the mesh dimension.
    """

    default_style = {
        "linewidth": 2,
        "marker": "o" if mesh.dim == 1 else None,
        "markersize": 3,
    }
    style = {**default_style, **kwargs}

    if 0 < mesh.dim < 3 and 0 <= dim < 3 and dim <= mesh.dim:
        if dim == 0 or dim == 1:
            for e in elements:
                x, y, _ = mesh.nodes[e, 0], mesh.nodes[e, 1], mesh.nodes[e, 2]
                ax.plot(x, y, **style)
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
