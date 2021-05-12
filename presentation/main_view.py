from datetime import datetime
from typing import Dict, List

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from domain.config import Config
from domain.model import MeshResults
from presentation.matrix_view import make_mesh_test_matrix_layout


def make_page_layout(mesh: MeshResults, results_timestamp: datetime, config: Config) -> html.Div:
    timestamp = results_timestamp.strftime("%H:%M:%S")
    header = f"Demo WebApp main page - test results timestamp {timestamp}"
    return html.Div(
        children=[
            html.H1(children=header, style={"textAlign": "center", "marginBottom": 50}),
            html.Div(html.Center("This is early prototype of SLA Web Application containing latency matrix")),
            html.H2(children="Demo Latency Matrix", style={"textAlign": "center", "marginTop": 100}),
            html.Div(
                make_mesh_test_matrix_layout(mesh, config),
                style={"marginLeft": 200, "marginRight": 200},
            ),
        ],
        style={"marginBottom": 50, "marginTop": 50, "marginLeft": 50, "marginRight": 50},
    )
