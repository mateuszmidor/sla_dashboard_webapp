import urllib.parse as urlparse
from typing import Tuple
from urllib.parse import parse_qs

import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

from domain.geo import calc_distance_in_kilometers
from domain.metric_type import MetricType
from domain.model import MeshResults
from domain.types import AgentID


class ChartView:
    @classmethod
    def make_layout(cls, from_agent, to_agent: AgentID, metric: MetricType, mesh: MeshResults) -> html.Div:
        title = cls.make_title(from_agent, to_agent, metric, mesh)
        xdata, ydata = zip(*mesh.filter(from_agent, to_agent, metric))
        fig = go.Figure(data=[go.Scatter(x=xdata, y=ydata)])

        return html.Div(
            children=[
                html.H1(children=title, style={"textAlign": "center", "marginBottom": 50}),
                dcc.Graph(id="timeseries_connection_chart", figure=fig),
                html.Center(dcc.Link("Back to matrix view", href="/")),
            ],
        )

    @staticmethod
    def make_title(from_agent, to_agent: AgentID, metric: MetricType, mesh: MeshResults) -> str:
        from_alias = mesh.agents.get_alias(from_agent)
        to_alias = mesh.agents.get_alias(to_agent)
        from_coords = mesh.agents.get_by_id(from_agent).coords
        to_coords = mesh.agents.get_by_id(to_agent).coords
        distance_km = calc_distance_in_kilometers(from_coords, to_coords)
        return f"{metric.value}: {from_alias} -> {to_alias} ({distance_km:.0f} km)"

    @staticmethod
    def encode_path(from_agent, to_agent: AgentID, metric: MetricType) -> str:
        return f"/chart?from={from_agent}&to={to_agent}&metric={metric.value}"

    @staticmethod
    def decode_path(path: str) -> Tuple[AgentID, AgentID, MetricType]:
        params = urlparse.parse_qs(urlparse.urlparse(path).query)
        return params["from"][0], params["to"][0], MetricType(params["metric"][0])
