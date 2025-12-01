import gmsh
import numpy as np

gmsh.initialize()

# Circle geometry
x, y = 0.0, 0.0
r = 1.0
p1 = gmsh.model.geo.addPoint(x + r, y, 0)
p2 = gmsh.model.geo.addPoint(x, y + r, 0)
p3 = gmsh.model.geo.addPoint(x - r, y, 0)
p4 = gmsh.model.geo.addPoint(x, y - r, 0)
center = gmsh.model.geo.addPoint(x, y, 0)

a1 = gmsh.model.geo.addCircleArc(p1, center, p2)
a2 = gmsh.model.geo.addCircleArc(p2, center, p3)
a3 = gmsh.model.geo.addCircleArc(p3, center, p4)
a4 = gmsh.model.geo.addCircleArc(p4, center, p1)
loop = gmsh.model.geo.addCurveLoop([a1, a2, a3, a4])
surface = gmsh.model.geo.addPlaneSurface([loop])
gmsh.model.geo.synchronize()
gmsh.model.mesh.generate(2)

# All nodes from the mesh
node_tags, node_coords, node_params = gmsh.model.mesh.getNodes()
nodes = node_coords.reshape(-1, 3)

# All elements from the mesh
elem_types, elem_tags, elem_node_tags = gmsh.model.mesh.getElements(2)
elements = elem_node_tags[0].reshape(-1, 2 + 1) - 1

used_node_tags = np.unique(np.concatenate(elem_node_tags))
print(nodes)
print(elements)
print(f"{len(nodes)} vs {len(used_node_tags)}")

print(min(np.concatenate(elem_node_tags)), max(np.concatenate(elem_node_tags)))


# Same with entities
entities = gmsh.model.getEntities(2)
entity_dim = entities[0][0]
tag = entities[0][1]
elem_types, elem_tags, elem_node_tags = gmsh.model.mesh.getElements(entity_dim, tag)
used_node_tags = np.unique(np.concatenate(elem_node_tags))
print(f"{len(nodes)} vs {len(used_node_tags)}")

print(min(np.concatenate(elem_node_tags)), max(np.concatenate(elem_node_tags)))
