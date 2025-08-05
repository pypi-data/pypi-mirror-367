from __future__ import annotations
from typing import Any, Optional, List, Type, TypeVar, Tuple
import numpy as np
from numpy.typing import NDArray

T = TypeVar('T')


class LogLevel:
    pass

class LogLevelCaps:
    def default(self) -> LogLevelCaps: ...

