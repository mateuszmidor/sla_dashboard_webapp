from typing import Dict, List

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from domain.model import MeshResults
from presentation.matrix_view import make_mesh_test_matrix_layout


def make_page_layout(mesh: MeshResults) -> html.Div:
    matrix = make_mesh_test_matrix_layout(mesh)
    return html.Div(
        children=[
            html.H1(children="Demo WebApp main page", style={"textAlign": "center", "marginBottom": 50}),
            html.Div(
                "This is early prototype of SLA Web Application containing latency matrix,"
                + " where lower latency limit was set to 300ms and higher limit was set to 400ms."
            ),
            html.H2(children="Demo Latency Matrix", style={"textAlign": "center", "marginTop": 100}),
            html.Div(make_mesh_test_matrix_layout(mesh), style={"marginLeft": 200, "marginRight": 200}),
        ],
        style={"marginBottom": 50, "marginTop": 50, "marginLeft": 50, "marginRight": 50},
    )
