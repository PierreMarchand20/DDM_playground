import logging
from dataclasses import dataclass, field

import numpy as np

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class MeshData:
    dim: int
    nodes: np.ndarray = field(default_factory=lambda: np.empty((0, 3)))
    elements: np.ndarray = field(default_factory=lambda: np.empty((0, 0), dtype=int))
    physical_group_elements: dict[str, np.ndarray] = field(default_factory=dict)
    partition_elements: dict[int, np.ndarray] = field(default_factory=dict)

    def __post_init__(self):
        # Ensure that elements has the right shape if empty
        if self.elements.size == 0:
            self.elements = np.empty((0, self.dim + 1), dtype=int)
