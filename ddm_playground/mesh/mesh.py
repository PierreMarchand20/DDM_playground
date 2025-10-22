import logging

logger = logging.getLogger(__name__)


class MeshData:
    def __init__(self, dim):
        self.dim = dim
        self.nodes = []
        self.elements = []
        self.boundary_elements = dict()
        self.partition_elements = dict()
