import dash
import dash_table

import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output

from domain.model import MeshResults
from presentation.matrix import Matrix


def make_mesh_test_matrix_layout(mesh: MeshResults):
    column_zero_header = {"name": "", "id": "agent_alias"}  # left-top table cell
    columns = [column_zero_header] + [{"name": row.alias, "id": row.alias} for row in mesh.rows]
    matrix = Matrix(mesh)
    data = []
    for row in mesh.rows:
        row_data = {"agent_alias": row.alias}
        for col in row.columns:
            latency_ms = matrix.cells[row.alias][col.alias].latency.value / 1000  # scale to milliseconds
            row_data[col.alias] = f"{latency_ms}ms"
        data.append(row_data)

    layout = dash_table.DataTable(id="table", columns=columns, data=data)
    return layout