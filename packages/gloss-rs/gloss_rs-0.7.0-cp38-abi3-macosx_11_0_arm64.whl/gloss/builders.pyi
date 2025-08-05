from __future__ import annotations
from typing import Any, Optional, List, Type, TypeVar, Tuple
import numpy as np
from numpy.typing import NDArray

T = TypeVar('T')


class EntityBuilder:
    def insert_to_entity(self, entity_bits: int, scene_ptr_idx: int) -> None: ...

class builders:
    def build_cube(self, center: NDArray[np.float32]) -> EntityBuilder: ...
    def build_floor(self) -> EntityBuilder: ...
    def build_from_file(self, path: str) -> EntityBuilder: ...

