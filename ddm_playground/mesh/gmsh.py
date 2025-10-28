import logging
import pathlib
from dataclasses import dataclass, field

import numpy as np

import gmsh
from ddm_playground.mesh.mesh import MeshData

logger = logging.getLogger(__name__)


@dataclass(kw_only=True, slots=True)
class GmshOptions:
    """GMSH options.

    Attributes
    ----------
    mesh_name : str, default mesh
        The name of the mesh to generate.
    element_order : int, optional, default 1
        The order of the elements.
    show_gui : bool, optional, default False
        Whether to show the GMSH GUI.
    terminal_output : bool, optional, default True
        Whether to enable terminal output.
    optimize_method : str | None, optional, default None
        The optimization method to use. If None, no optimization is performed.
        See GMSH documentation for available methods.
    renumber_nodes : str | None, optional, default "RCMK"
        The renumbering method to use. If None, no renumbering is performed.
        See GMSH documentation for available methods.
    """

    mesh_name: str = "mesh"
    element_order: int = 1
    show_gui: bool = False
    terminal_output: bool = False
    optimize_method: str | None = None
    renumber_nodes: str | None = "RCMK"


@dataclass(slots=True)
class GmshContextManager:
    """Context manager for GMSH.

    Attributes
    ----------
    options : GmshOptions, optional, default GmshOptions()
    """

    options: GmshOptions = field(default_factory=GmshOptions)

    def generate(self, dim=2, partition: int | None = None):
        gmsh.model.mesh.generate(dim)

        return self._extract_mesh_data(dim, partition)

    def _extract_mesh_data(self, dim, partition):
        mesh = MeshData(dim)

        # All nodes from the mesh
        node_tags, node_coords, node_params = gmsh.model.mesh.getNodes()

        # All elements from the mesh
        _, elem_tags, elem_node_tags = gmsh.model.mesh.getElements(dim)

        # Get used nodes indexes, removing possibly node only used for defining the geometry
        used_node_tags = np.unique(np.concatenate(elem_node_tags))

        # Map tags to new node indexes
        node_tag_to_new_index = {tag: i for i, tag in enumerate(used_node_tags)}

        # Map tags to old node indexes
        tag_to_full_index = {tag: i for i, tag in enumerate(node_tags)}
        used_indices = np.array([tag_to_full_index[t] for t in used_node_tags])
        mesh.nodes = node_coords.reshape(-1, 3)[used_indices]

        # Reindex elements, WARNING, no need to -1 because of reindexing
        new_elem_node_tags = [
            np.array([node_tag_to_new_index[t] for t in elem_nodes])
            for elem_nodes in elem_node_tags
        ]
        mesh.elements = new_elem_node_tags[0].reshape(-1, dim + 1)

        # Elements from user-defined physical groups
        physical_groups = gmsh.model.getPhysicalGroups()
        for dim_pg, tag_pg in physical_groups:
            name = gmsh.model.getPhysicalName(dim_pg, tag_pg)
            _, elem_tags, elem_node_tags = gmsh.model.mesh.getElements(dim_pg, tag_pg)
            if elem_node_tags:
                n_nodes_per_elem = len(elem_node_tags[0]) // len(elem_tags[0])
                new_elem_node_tags = [
                    np.array([node_tag_to_new_index[t] for t in elem_nodes])
                    for elem_nodes in elem_node_tags
                ]
                mesh.physical_group_elements[(name, dim_pg, tag_pg)] = (
                    new_elem_node_tags[0].reshape(-1, n_nodes_per_elem)
                )

        if partition and partition > 1:
            gmsh.model.mesh.partition(partition)  # metis partition

        # Get information from partitions
        entities = gmsh.model.getEntities(dim)
        for e in entities:
            entity_dim = e[0]
            tag = e[1]

            partitions = gmsh.model.getPartitions(e[0], e[1])
            if len(partitions) and dim == entity_dim:
                logging.info(
                    "Entity " + str(e) + " of type " + gmsh.model.getType(e[0], e[1])
                )
                logging.info(" - Partition(s): " + str(partitions))
                logging.info(" - Parent: " + str(gmsh.model.getParent(e[0], e[1])))
                logging.info(" - Boundary: " + str(gmsh.model.getBoundary([e])))

                partition_id = tag % partition

                # Get the mesh elements for the partition:
                elem_types, elem_tags, elem_node_tags = gmsh.model.mesh.getElements(
                    entity_dim, tag
                )

                #
                new_elem_node_tags = [
                    np.array([node_tag_to_new_index[t] for t in elem_nodes])
                    for elem_nodes in elem_node_tags
                ]
                mesh.partitions_elements[partition_id] = new_elem_node_tags[0].reshape(
                    -1, dim + 1
                )

        return mesh

    def __enter__(self):
        gmsh.initialize()
        gmsh.model.add(self.options.mesh_name)
        gmsh.option.set_number("General.Terminal", int(self.options.terminal_output))
        gmsh.option.set_number("Mesh.ElementOrder", self.options.element_order)

        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        gmsh.finalize()

    def write(self, path: pathlib.Path):
        gmsh.write(path)
        logger.info(f"Mesh written to {path}")

    def fltk(self):
        gmsh.fltk.run()
