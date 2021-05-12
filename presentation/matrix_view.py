from typing import Dict, List

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output

from domain.config import Config
from domain.model import MeshResults
from presentation.matrix import Matrix


def make_mesh_test_matrix_layout(mesh: MeshResults, config: Config) -> dash_table.DataTable:
    column_zero_header = {"name": "", "id": "agent_alias"}  # left-top table cell
    columns = [column_zero_header] + [{"name": row.alias, "id": row.alias} for row in mesh.rows]
    matrix = Matrix(mesh)
    data = make_data(mesh, matrix)
    styles = make_colors(mesh, config.latency_deteriorated_ms, config.latency_failed_ms)
    return dash_table.DataTable(
        id="table",
        columns=columns,
        style_cell={"textAlign": "center"},
        data=data,
        style_data_conditional=styles,
    )


def make_data(mesh: MeshResults, matrix: Matrix) -> List[Dict]:
    data = []
    for row in mesh.rows:
        row_data = {"agent_alias": row.alias}
        for col in row.columns:
            latency_ms = matrix.cells[row.alias][col.alias].latency_microsec.value / 1000  # scale to milliseconds
            row_data[col.alias] = f"{latency_ms} ms"
        data.append(row_data)
    return data


def make_colors(mesh: MeshResults, latency_deteriorated_ms: int, latency_failed_ms: int):
    styles = []
    for index, row in enumerate(mesh.rows):
        for column in row.columns:
            if column.latency_microsec.value > latency_failed_ms * 1000:
                styles.append(
                    {
                        "if": {
                            "column_id": column.alias,
                            "row_index": index,
                        },
                        "backgroundColor": "red",
                    }
                )
            elif column.latency_microsec.value > latency_deteriorated_ms * 1000:
                styles.append(
                    {
                        "if": {
                            "column_id": column.alias,
                            "row_index": index,
                        },
                        "backgroundColor": "orange",
                    }
                )
            else:
                styles.append(
                    {
                        "if": {
                            "column_id": column.alias,
                            "row_index": index,
                        },
                        "backgroundColor": "green",
                    }
                )

    return styles
