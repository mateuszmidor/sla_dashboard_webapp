import urllib.parse as urlparse
from typing import List, Tuple
from urllib.parse import parse_qs

import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

from domain.metric_type import MetricType
from domain.model import MeshResults
from domain.model.mesh_results import HealthItem, MeshResults
from domain.types import AgentID, MetricValue
from presentation.localtime import utc_to_localtime


class ChartView:
    @staticmethod
    def make_layout(from_agent, to_agent: AgentID, metric: MetricType, results: MeshResults) -> html.Div:
        # make chart title
        from_alias = results.agents.get_alias(from_agent)
        to_alias = results.agents.get_alias(to_agent)
        title = f"{metric.value}: {from_alias} -> {to_alias}"

        # make chart data
        xdata, ydata = zip(*results.filter(from_agent, to_agent, metric))
        fig = go.Figure(data=[go.Scatter(x=xdata, y=ydata)])

        return html.Div(
            children=[
                html.H1(children=title, style={"textAlign": "center", "marginBottom": 50}),
                dcc.Graph(id="timeseries_connection_chart", figure=fig),
                html.Center(dcc.Link("Back to matrix view", href="/")),
            ],
        )

    @staticmethod
    def encode_path(from_agent, to_agent: AgentID, metric: MetricType) -> str:
        return f"/chart?from={from_agent}&to={to_agent}&metric={metric.value}"

    @staticmethod
    def decode_path(path: str) -> Tuple[AgentID, AgentID, MetricType]:
        params = urlparse.parse_qs(urlparse.urlparse(path).query)
        return params["from"][0], params["to"][0], MetricType(params["metric"][0])
