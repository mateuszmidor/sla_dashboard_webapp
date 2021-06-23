import urllib.parse as urlparse
from typing import Optional, Tuple
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
        fig_packetloss = cls.make_figure(from_agent, to_agent, MetricType.PACKET_LOSS, mesh, (0, 100))
        style = {"width": "100%", "height": "20vh", "display": "inline-block", "margin-bottom": "20px"}
        return html.Div(
            children=[
                html.H1(children=title, className="header_main"),
                html.Div(
                    children=[
                        html.H3(children=MetricType.LATENCY.value, className="chart_title"),
                        dcc.Graph(id="timeseries_latency_chart", style=style, figure=fig_latency),
                        html.H3(children=MetricType.JITTER.value, className="chart_title"),
                        dcc.Graph(id="timeseries_jitter_chart", style=style, figure=fig_jitter),
                        html.H3(children=MetricType.PACKET_LOSS.value, className="chart_title"),
                        dcc.Graph(id="timeseries_packetloss_chart", style=style, figure=fig_packetloss),
                        html.Div(
                            html.Center(dcc.Link("Back to matrix view", href="/"), style={"font-size": "large"}),
                            className="button",
                        ),
                    ],
                    className="main_container",
                ),
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
    def make_figure(
        from_agent,
        to_agent: AgentID,
        metric: MetricType,
        mesh: MeshResults,
        y_range: Optional[Tuple[float, float]] = None,
    ):
        filtered = mesh.filter(from_agent, to_agent, metric)
        xdata, ydata = zip(*filtered) if filtered else ((), ())
        layout = go.Layout(margin={"t": 0, "b": 0})  # remove empty space above and below the chart
        fig = go.Figure(
            data=[go.Scatter(x=xdata, y=ydata)],
            layout=layout,
            layout_yaxis_range=y_range,
        )
        fig.update_yaxes(rangemode="tozero")  # make the y-scale start from 0
        return fig

    @staticmethod
    def encode_path(from_agent, to_agent: AgentID) -> str:
        return f"/chart?from={from_agent}&to={to_agent}"

    @staticmethod
    def decode_path(path: str) -> Tuple[AgentID, AgentID]:
        params = urlparse.parse_qs(urlparse.urlparse(path).query)
        return params["from"][0], params["to"][0]
