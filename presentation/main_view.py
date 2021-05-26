from datetime import datetime

import dash
import dash_core_components as dcc
import dash_html_components as html

from domain.config import Config
from domain.model import MeshResults


def make_page_layout(mesh: MeshResults, results_timestamp: datetime, config: Config) -> html.Div:
    timestamp = results_timestamp.strftime("%H:%M:%S")
    header = "SLA Dashboard"
    return html.Div(
        children=[
            html.H1(children=header, style={"textAlign": "center", "marginBottom": 50}),
            html.H2(
                f"Latency/Jitter/Loss Matrix - data timestamp {timestamp}",
                style={"textAlign": "center", "marginTop": 100},
            ),
            html.Center("Select primary metric: "),
            dcc.Dropdown(
                id="metric-selector",
                options=[
                    {"label": "Latency [ms]", "value": "latency"},
                    {"label": "Jitter [ms]", "value": "jitter"},
                    {"label": "Packet loss %", "value": "loss"},
                ],
                value="latency",
                clearable=False,
                style={"width": 450, "margin-left": "auto", "margin-right": "auto"},
            ),
            html.Div(
                html.Center(
                    dcc.Graph(id="matrix", style={"width": 750, "height": 750}),
                    style={"marginLeft": 200, "marginRight": 200},
                ),
            ),
        ],
        style={"marginBottom": 50, "marginTop": 50, "marginLeft": 50, "marginRight": 50},
    )
