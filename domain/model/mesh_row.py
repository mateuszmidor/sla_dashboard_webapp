from dataclasses import dataclass
from typing import List

from domain.model.mesh_column import MeshColumn


@dataclass
class MeshRow:
    name: str
    alias: str
    id: str
    ip: str
    local_ip: str
    columns: List[MeshColumn]
