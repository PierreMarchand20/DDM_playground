Installation
------------

Either download or git clone this repository

.. code-block:: bash

    git clone https://github.com/PierreMarchand20/DDM_playground.git && cd DDM_playground

In the folder of this repository, do:

.. code-block:: bash

    pip install .


Mesh generation
---------------

To generate a mesh, and optionally its partition, you can use the context manager :py:class:`~ddm_playground.mesh.gmsh.GmshContextManager` which defines the correct environment to call `GMSH`_ API to define your geometry. In the following example, where we define a 1D line, a mesh generator is defined line 6, and is used line 16 to generate the mesh and its partition.


.. literalinclude:: ../../examples/simple_mesh.py
   :language: python
   :linenos:
   :emphasize-lines: 9,16

The resulting :code:`mesh` variable is a :py:class:`~ddm_playground.mesh.data.MeshData` object containing

- the nodes and elements of the mesh generated with `GMSH`_,
- the elements of the partitions created by `METIS`_ via `GMSH`_ and stored in a dictionnary whose keys are the partitions numbers.

Domain decomposition with overlap
---------------------------------

From a partition stored in a :py:class:`~ddm_playground.mesh.data.MeshData` object, a domain decomposition with overlap and meshes associated to each subdomain can be created with a simple call to :py:class:`~ddm_playground.mesh.overlap.add_overlap`.

.. literalinclude:: ../../examples/overlap.py
   :language: python
   :lines: 53-55

Outputs are

- :code:`submeshes`: a dictionnary whose keys are the subdomains numbers, and values are their associated :py:class:`~ddm_playground.mesh.data.MeshData`. In particular, it contains the restriction to their physical groups, and a new physical group corresponding to the new boundary of the subdomain called "interface".
- :code:`neighbors`: a dictionnary whose keys are the subdomains numbers, and values are arrays containing the subdomains numbers corresponding of the neighboring subdomains.
- :code:`intersections`: a dictionnary whose keys are the subdomains numbers, and values are the list of the local nodes shared with each neighbors.
- :code:`partition_of_unity`: a dictionnary whose keys are the subdomains numbers, and values are local arrays to the subdomain defining a partition of unity. 
