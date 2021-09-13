from dataclasses import dataclass

from domain.types import MatrixCellColor


@dataclass(frozen=True)
class Matrix:
    cell_color_healthy: MatrixCellColor
    cell_color_warning: MatrixCellColor
    cell_color_critical: MatrixCellColor
    cell_color_nodata: MatrixCellColor
