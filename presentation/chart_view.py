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
    def make_layout(cls, from_agent, to_agent: AgentID, mesh: MeshResults) -> html.Div:
        title = cls.make_title(from_agent, to_agent, mesh)
        fig_latency = cls.make_figure(from_agent, to_agent, MetricType.LATENCY, mesh)
        fig_jitter = cls.make_figure(from_agent, to_agent, MetricType.JITTER, mesh)
        fig_packetloss = cls.make_figure(from_agent, to_agent, MetricType.PACKET_LOSS, mesh)
        return html.Div(
            children=[
                html.H1(children=title, style={"textAlign": "center", "marginBottom": 50}),
                html.H3(children=MetricType.LATENCY.value),
                dcc.Graph(id="timeseries_latency_chart", figure=fig_latency),
                html.H3(children=MetricType.JITTER.value),
                dcc.Graph(id="timeseries_jitter_chart", figure=fig_jitter),
                html.H3(children=MetricType.PACKET_LOSS.value),
                dcc.Graph(id="timeseries_packetloss_chart", figure=fig_packetloss),
                html.Center(dcc.Link("Back to matrix view", href="/")),
            ],
        )

    @staticmethod
    def make_title(from_agent, to_agent: AgentID, mesh: MeshResults) -> str:
        from_alias = mesh.agents.get_alias(from_agent)
        to_alias = mesh.agents.get_alias(to_agent)
        from_coords = mesh.agents.get_by_id(from_agent).coords
        to_coords = mesh.agents.get_by_id(to_agent).coords
        distance_km = calc_distance_in_kilometers(from_coords, to_coords)
        return f"{from_alias} -> {to_alias} ({distance_km:.0f} km)"

    @staticmethod
    def make_figure(from_agent, to_agent: AgentID, metric: MetricType, mesh: MeshResults):
        xdata, ydata = zip(*mesh.filter(from_agent, to_agent, metric))
        return go.Figure(data=[go.Scatter(x=xdata, y=ydata)])

    @staticmethod
    def encode_path(from_agent, to_agent: AgentID) -> str:
        return f"/chart?from={from_agent}&to={to_agent}"

    @staticmethod
    def decode_path(path: str) -> Tuple[AgentID, AgentID]:
        params = urlparse.parse_qs(urlparse.urlparse(path).query)
        return params["from"][0], params["to"][0]
