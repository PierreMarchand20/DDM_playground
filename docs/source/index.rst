DDM_playground
==============

DDM_playground is a lightweight Python package to support domain decomposition methods. It provides

- a `GMSH`_ context manager :py:class:`~ddm_playground.mesh.gmsh.GmshContextManager`,
- a data class for a mesh and its partition (without overlap) :py:class:`~ddm_playground.mesh.data.MeshData`,
- a utility fonction to add overlap to a partitioned mesh :py:class:`~ddm_playground.mesh.overlap.add_overlap`,
- utility functions to plot with meshes, and submeshes (of dimension lower or equal to initial mesh) with `matplotlib`_, respectively :py:class:`~ddm_playground.mesh.plot.plot_mesh` and :py:class:`~ddm_playground.mesh.plot.plot_submesh`.

.. raw:: latex

         \tableofcontents
         
.. only:: not latex

   **Contents**

.. toctree::
   :maxdepth: 2
   
   introduction
   ddm_playground
   PDF version <https://pmarchand.pages.math.cnrs.fr/ddm_playground_documentation/ddm_playground.pdf>



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
