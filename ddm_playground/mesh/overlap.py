import copy
from collections import defaultdict

import numpy as np

from ddm_playground.mesh.data import MeshData


def add_overlap(
    mesh: MeshData, overlap: int
) -> tuple[
    dict[int, MeshData],
    dict[int, list[int]],
    dict[int, list[list[int]]],
    dict[int, np.ndarray],
    dict[int, np.ndarray],
]:
    r"""
    Build overlapping subdomains from a partitioned mesh.

    This function takes an existing mesh with disjoint partitions
    and extends each partition by a given number of element layers
    (`overlap`) to create overlapping subdomains. It also computes:

    - the neighboring partitions,
    - the local-to-global node mappings,
    - and the intersections between overlapping subdomains.

    Parameters
    ----------
    mesh : MeshData
        Global mesh object containing:
          - node coordinates (`mesh.nodes`)
          - element connectivity (`mesh.elements`)
          - partition definitions (`mesh.partitions_elements`)
    overlap : int
        Number of layers of neighboring elements to include
        around each partition (i.e., the "overlap" thickness).

    Returns
    -------
    meshes : dict[int, MeshData]
        Dictionary of `MeshData` objects for each overlapping subdomain.
        Each subdomain contains its own local nodes, elements, and
        restricted physical groups. They also have a new physical group called
        "interface", corresponding to its boundary not included in the boundary of
        the initial mesh.

    neighbors : dict[int, list[int]]
        For each partition ID, list of neighboring partition IDs
        that share an overlapping region.

    intersections : dict[int, list[list[int]]]
        For each partition ID, list of intersections with each neighbor.
        Each intersection is represented as a list of *local node indices*
        within the overlapping subdomain.

    partition_of_unity : dict[int, np.ndarray]
        For each subdomain :math:`i`, array containing the local partition of unity.
        Each array corresponds to the diagonal matrix :math:`\mathbf{D}_i`, 
        whose diagonal entries are defined as

        .. math::

            (\mathbf{D}_i)_{k,k}=
            \left\{
            \begin{aligned}
            \frac{1}{c_k}& \quad \text{if the } k \text{-th node belongs to a partition without overlap,} \\
            0 &\quad \text{otherwise.}
            \end{aligned}
            \right.

        Here, :math:`c_k` denotes the number of partitions in which the :math:`k` th node appears.

    ovr_subdomain_to_global : dict[int, np.ndarray]
        For each subdomain, array mapping local node indices
        to their global indices in the original mesh.

    Notes
    -----
    The overlap expansion is performed iteratively using boolean masks:
      - From nodes → elements (P1 → P0)
      - From elements → nodes (P0 → P1)

    The algorithm proceeds as follows:
      1. Identify nodes belonging to each initial partition.
      2. Expand the partition by `overlap` layers of neighboring elements.
      3. Detect neighboring partitions by searching nodes that belong
         to multiple expanded regions.
      4. Build new MeshData objects restricted to each subdomain.
      5. Extract local interfaces (boundaries touching other partitions).
      6. Compute intersection regions between overlapping subdomains.
    """
    nb_nodes = len(mesh.nodes)
    global_elements = mesh.elements
    nb_elements = global_elements.shape[0]
    n_nodes_per_elem = global_elements.shape[1]
    nb_partitions = len(mesh.partitions_elements.keys())

    # Initial partition
    initial_nodes_partition: dict[int, np.ndarray] = dict()
    for partition_id, partition_elements in mesh.partitions_elements.items():
        #  Tag nodes with partition id
        initial_nodes_partition[partition_id] = np.full(
            (nb_nodes), fill_value=False, dtype=bool
        )
        for elt in partition_elements:
            for index in elt:
                initial_nodes_partition[partition_id][index] = True
    #
    neighbors_sets: dict[int, set] = defaultdict(set)
    neighbors: dict[int, list] = dict()
    nodes_partition: dict[int, np.ndarray] = dict()
    intersections: dict[int, list[list]] = dict()
    partition_of_unity: dict[int, np.ndarray] = dict()
    global_to_ovr_subdomain: dict[int, np.ndarray] = dict()
    partition_to_ovr_subdomain: dict[int, np.ndarray] = dict()
    ovr_subdomain_to_global: dict[int, np.ndarray] = dict()
    elements_in_subdomain: dict[int, np.ndarray] = dict()
    meshes: dict[int, MeshData] = dict()

    for partition_id, _ in mesh.partitions_elements.items():
        nodes_partition[partition_id] = copy.deepcopy(
            initial_nodes_partition[partition_id]
        )
        elements_partition = np.full((nb_elements), fill_value=False, dtype=bool)
        for _ in range(overlap):
            #  Tag elements including part_overlap's nodes: P1 -> P0
            for j in range(nb_elements):
                for k in range(n_nodes_per_elem):
                    # if global_elements[j, k] >= 0:
                    elements_partition[j] = (
                        elements_partition[j]
                        or (nodes_partition[partition_id][global_elements[j, k]])
                    )

            #  Tag nodes including elements from elts : P0 -> P1
            for j in range(nb_elements):
                for k in range(n_nodes_per_elem):
                    # if global_elements[j, k] >= 0:
                    nodes_partition[partition_id][global_elements[j, k]] = (
                        nodes_partition[partition_id][global_elements[j, k]]
                        or elements_partition[j]
                    )

        # We go twice as far to find neighbours
        node_partition_find_neighbors = copy.deepcopy(nodes_partition[partition_id])
        elements_partition_find_neighbors = copy.deepcopy(elements_partition)
        for _ in range(overlap):
            for j in range(nb_elements):
                for k in range(n_nodes_per_elem):
                    # if global_elements[j, k] >= 0:
                    elements_partition_find_neighbors[j] = (
                        elements_partition_find_neighbors[j]
                        or (node_partition_find_neighbors[global_elements[j, k]])
                    )

            for j in range(nb_elements):
                for k in range(n_nodes_per_elem):
                    # if global_elements[j, k] >= 0:
                    node_partition_find_neighbors[global_elements[j, k]] = (
                        node_partition_find_neighbors[global_elements[j, k]]
                        or elements_partition_find_neighbors[j]
                    )

        for user_dof in range(nb_nodes):
            if node_partition_find_neighbors[user_dof]:
                for partition_index in range(nb_partitions):
                    if (
                        partition_index != partition_id
                        and initial_nodes_partition[partition_index][user_dof]
                    ):
                        neighbors_sets[partition_id].add(partition_index)

        neighbors[partition_id] = list(neighbors_sets[partition_id])

        #  Get the global to overlapping subdomain numbering
        global_to_ovr_subdomain[partition_id] = np.full(
            (nb_nodes), fill_value=-1, dtype=int
        )
        count = 0
        for user_dof in range(nb_nodes):
            if nodes_partition[partition_id][user_dof]:
                global_to_ovr_subdomain[partition_id][user_dof] = count
                count = count + 1

        # Get the partition to overlapping subdomain numbering
        partition_to_ovr_subdomain[partition_id] = global_to_ovr_subdomain[
            partition_id
        ][np.where(initial_nodes_partition[partition_id])[0]]

        # Get the elements on the subdomain
        nb_elements_on_subdomain = elements_partition.sum()
        elements_in_subdomain[partition_id] = np.full(
            (nb_elements_on_subdomain, global_elements.shape[1]),
            fill_value=np.zeros(n_nodes_per_elem),
            dtype=int,
        )
        count = 0
        for user_elt in range(nb_elements):
            if elements_partition[user_elt]:
                elements_in_subdomain[partition_id][count] = global_to_ovr_subdomain[
                    partition_id
                ][global_elements[user_elt]]
                count = count + 1

        # Get the overlapping subdomain to global numbering
        size_ovr_subdomain = sum(nodes_partition[partition_id])
        ovr_subdomain_to_global[partition_id] = np.full(
            (size_ovr_subdomain), fill_value=-1, dtype=int
        )
        for user_dof in range(nb_nodes):
            if global_to_ovr_subdomain[partition_id][user_dof] != -1:
                ovr_subdomain_to_global[partition_id][
                    global_to_ovr_subdomain[partition_id][user_dof]
                ] = user_dof

        # Set MeshData
        meshes[partition_id] = MeshData(
            mesh.dim,
            mesh.nodes[ovr_subdomain_to_global[partition_id][:]],
            elements_in_subdomain[partition_id],
        )

        # Restrict physical groups to subdomain
        for physical_group_name, elements in mesh.physical_group_elements.items():
            new_elements = []
            for element in elements:
                if np.all(global_to_ovr_subdomain[partition_id][element[:]] != -1):
                    new_elements.append(
                        global_to_ovr_subdomain[partition_id][element[:]]
                    )
            if len(new_elements) != 0:
                meshes[partition_id].physical_group_elements[physical_group_name] = (
                    np.array(new_elements)
                )

        # Compute interface
        elements_on_interface = []
        for j in range(nb_elements):
            for k in range(n_nodes_per_elem):
                # If new element
                if (
                    not elements_partition[j]
                    and np.sum(nodes_partition[partition_id][global_elements[j, :]])
                    == mesh.dim
                ):
                    mask = nodes_partition[partition_id][global_elements[j, :]]
                    elements_on_interface.append(
                        global_to_ovr_subdomain[partition_id][global_elements[j, mask]]
                    )

                elements_partition[j] = (
                    elements_partition[j]
                    or (nodes_partition[partition_id][global_elements[j, k]])
                )
        # print(elements_on_interface)
        meshes[partition_id].physical_group_elements[
            ("interface", mesh.dim - 1, None)
        ] = np.array(elements_on_interface)

        # Increase overlap in each neighbor domain
        intersections[partition_id] = []
        for neighbor_index in neighbors[partition_id]:
            part_overlap_neighbors = np.full((nb_nodes), fill_value=False, dtype=bool)
            for user_dof in range(nb_nodes):
                part_overlap_neighbors[user_dof] = initial_nodes_partition[
                    neighbor_index
                ][user_dof]

            for _ in range(0, overlap):
                # Tag des elements qui contiennent les dofs du voisin: P1 -> P0
                elements_partition.fill(False)

                for j in range(nb_elements):
                    for k in range(n_nodes_per_elem):
                        # if elemConnectivity[j, k] >= 0:
                        elements_partition[j] = (
                            elements_partition[j]
                            or (part_overlap_neighbors[global_elements[j, k]])
                        )

                #  Tag de mes dofs qui sont contenus dans les elements: P0 -> P1
                for j in range(nb_elements):
                    for k in range(n_nodes_per_elem):
                        # if elemConnectivity[j, k] >= 0:
                        part_overlap_neighbors[global_elements[j, k]] = (
                            part_overlap_neighbors[global_elements[j, k]]
                            or elements_partition[j]
                        )

            part_overlap_neighbors = (
                nodes_partition[partition_id] & part_overlap_neighbors
            )
            intersection = []
            test = []
            for i in range(0, nb_nodes):
                if part_overlap_neighbors[i]:
                    intersection.append(global_to_ovr_subdomain[partition_id][i])
                    test.append(i)
            intersections[partition_id].append(intersection)

    node_multiplicity = np.full(len(mesh.nodes), fill_value=0, dtype=int)
    for partition_elements in mesh.partitions_elements.values():
        node_multiplicity[np.unique(np.concatenate(partition_elements))[:]] += 1

    for subdomain_id, subdomain in meshes.items():
        partition_of_unity[subdomain_id] = np.full(
            len(subdomain.nodes), fill_value=0, dtype=float
        )
        temp = np.full(
            len(partition_to_ovr_subdomain[subdomain_id]), fill_value=0, dtype=float
        )
        temp = (
            1.0
            / node_multiplicity[
                ovr_subdomain_to_global[subdomain_id][
                    partition_to_ovr_subdomain[subdomain_id][:]
                ]
            ]
        )
        partition_of_unity[subdomain_id][
            partition_to_ovr_subdomain[subdomain_id][:]
        ] = temp

    return (
        meshes,
        neighbors,
        intersections,
        partition_of_unity,
        ovr_subdomain_to_global,
    )
