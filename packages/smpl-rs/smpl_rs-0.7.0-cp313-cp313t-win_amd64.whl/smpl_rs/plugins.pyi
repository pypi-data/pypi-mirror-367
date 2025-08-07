from __future__ import annotations
from typing import Any, Optional, List, Type, TypeVar, Tuple, Union
import numpy as np
from numpy.typing import NDArray

T = TypeVar('T')


class SmplPlugin:
    def insert_plugin(self, plugin_ptr_idx: int) -> None: ...

