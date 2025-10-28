import logging
from dataclasses import dataclass, field

import numpy as np

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class MeshData:
    """
    Container for finite element mesh data.

    This class stores geometric and topological information about a mesh,
    such as node coordinates, element connectivity, and metadata about
    physical groups or domain partitions.

    Attributes
    ----------
    dim : int
        The spatial dimension of the mesh (e.g. 1, 2, or 3).

    nodes : np.ndarray
        Array of nodal coordinates with shape (n_nodes, 3).
        Only the first `dim` columns are used; extra columns can
        hold padding zeros for uniformity.

    elements : np.ndarray
        Integer array of shape (n_elements, n_vertices_per_element)
        containing node indices that define each element's connectivity.
        The number of vertices per element is typically `dim + 1`
        for simplicial meshes (lines, triangles, tetrahedra).

    physical_group_elements : dict[tuple[str, int, int | None], np.ndarray]
        Mapping that associates groups of elements with a physical tag.
        The key is a tuple `(group_name, group_dim, group_tag)` where:
            - `group_name` (str): descriptive label (e.g. "boundary", "interface").
            - `group_dim` (int): dimension of the elements in the physical group.
            - `group_tag` (int | None): optional identifier.
        The value is an array of element indices belonging to that group.

    partitions_elements : dict[int, np.ndarray]
        Partitioned subdomains of the mesh.
        Maps a partition ID (int) to the array of element indices associated with the subdomain.

    Methods
    -------
    __post_init__():
        Ensures internal consistency of empty arrays. If `elements`
        is empty, it is reshaped to have the correct second dimension
        based on `dim` (i.e. `dim + 1` columns for simplicial elements).
    """

    dim: int
    nodes: np.ndarray = field(default_factory=lambda: np.empty((0, 3)))
    elements: np.ndarray = field(default_factory=lambda: np.empty((0, 0), dtype=int))
    physical_group_elements: dict[tuple[str, int, int | None], np.ndarray] = field(
        default_factory=dict
    )
    partitions_elements: dict[int, dict[str, np.ndarray]] = field(default_factory=dict)

    def __post_init__(self):
        # Ensure that elements has the right shape if empty
        if self.elements.size == 0:
            self.elements = np.empty((0, self.dim + 1), dtype=int)
