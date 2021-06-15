import itertools
from datetime import datetime
from typing import Dict, List, Optional

import dash_core_components as dcc
import dash_html_components as html

from domain.config import Config
from domain.config.thresholds import Thresholds
from domain.geo import calc_distance_in_kilometers
from domain.metric_type import MetricType
from domain.model import MeshResults
from domain.model.mesh_results import MeshColumn
from domain.types import MetricValue, Threshold
from presentation.localtime import utc_to_localtime


class MatrixView:
    MATRIX = "matrix"
    METRIC_SELECTOR = "metric-selector"

    @classmethod
    def make_layout(cls, mesh: MeshResults, metric: MetricType) -> html.Div:
        localtime_timestamp = utc_to_localtime(mesh.utc_timestamp)
        timestamp = localtime_timestamp.strftime("%x %X")
        header = "SLA Dashboard"
        return html.Div(
            children=[
                html.H1(children=header, className="header_main"),
                html.Div(children=[
                      html.H2(f"Data timestamp {timestamp}", className="header__subTitle"),
                      html.Div(
                          children=[
                              html.Label("Select primary metric:", className="select_label"),
                              dcc.Dropdown(
                                  id=cls.METRIC_SELECTOR,
                                  options=[
                                      {"label": "Latency [ms]", "value": MetricType.LATENCY.value},
                                      {"label": "Jitter [ms]", "value": MetricType.JITTER.value},
                                      {"label": "Packet loss [%]", "value": MetricType.PACKET_LOSS.value},
                                  ],
                                  value=metric.value,
                                  clearable=False,
                                  className="dropdowns"
                              )
                          ], className="select_container"
                      ),
                      html.Div(
                          html.Div(
                               dcc.Graph(id=cls.MATRIX, style={"width": 900, "height": 750}),
                               className="chart__default"
                          )
                      )
                ], className="main_container")
            ],
        )

    @classmethod
    def make_matrix_data(cls, mesh: MeshResults, metric: MetricType, config: Config) -> Dict:
        data = cls.make_data(mesh, metric, cls.get_thresholds(metric, config))
        annotations = cls.make_annotations(mesh, metric)
        layout = dict(
            margin=dict(l=150, b=50, t=100, r=50),
            modebar={"orientation": "v"},
            annotations=annotations,
            xaxis=dict(side="top", ticks="", scaleanchor="y"),
            yaxis=dict(side="left", ticks=""),
            hovermode="closest",
            showlegend=False,
        )

        return {"data": data, "layout": layout}

    @staticmethod
    def get_thresholds(metric: MetricType, config: Config) -> Thresholds:
        if metric == MetricType.LATENCY:
            return config.latency
        elif metric == MetricType.JITTER:
            return config.jitter
        else:
            return config.packet_loss

    @classmethod
    def make_data(cls, mesh: MeshResults, metric: MetricType, tresholds: Thresholds) -> List[Dict]:
        colors = cls.make_colors(mesh, metric, tresholds)
        labels = [mesh.agents.get_by_id(row.agent_id).alias for row in mesh.rows]
        reversed_labels = list(reversed(labels))
        return [
            dict(
                x=labels,
                y=reversed_labels,
                z=colors,
                text=cls.make_hover_text(mesh),
                type="heatmap",
                hoverinfo="text",
                opacity=1,
                name="",
                showscale=False,
                colorscale=cls.get_colorscale(colors),
            )
        ]

    @classmethod
    def make_colors(cls, mesh: MeshResults, metric: MetricType, tresholds: Thresholds) -> List[List]:
        Col = List[Optional[float]]
        colors: List[Col] = []
        for row in reversed(mesh.rows):
            colors_col: Col = []
            for col in row.columns:
                warning = tresholds.warning(row.agent_id, col.agent_id)
                error = tresholds.error(row.agent_id, col.agent_id)
                value = cls.get_metric_value(metric, mesh.connection(row.agent_id, col.agent_id))
                color = cls.get_color(value, warning, error)
                colors_col.append(color)
            colors.append(colors_col)

        for i in range(len(mesh.rows)):  # add Nones at diagonal to avoid colorising it
            colors[-(i + 1)].insert(i, None)

        return colors

    @staticmethod
    def get_metric_value(metric: MetricType, cell: MeshColumn) -> MetricValue:
        if metric == MetricType.LATENCY:
            return cell.latency_millisec.value
        elif metric == MetricType.JITTER:
            return cell.jitter_millisec.value
        else:
            return cell.packet_loss_percent.value

    @classmethod
    def make_annotations(cls, mesh: MeshResults, metric: MetricType) -> List[Dict]:
        annotations = []
        for row in reversed(mesh.rows):
            for col in row.columns:
                from_agent = mesh.agents.get_by_id(row.agent_id)
                to_agent = mesh.agents.get_by_id(col.agent_id)
                text = cls.get_text(metric, mesh.connection(from_agent.id, to_agent.id))
                annotations.append(
                    dict(
                        showarrow=False,
                        text=text,
                        xref="x",
                        yref="y",
                        x=to_agent.alias,
                        y=from_agent.alias,
                    )
                )
        return annotations

    @staticmethod
    def get_text(metric: MetricType, cell: MeshColumn) -> str:
        if metric == MetricType.LATENCY:
            return f"<b>{(cell.latency_millisec.value):.2f} ms</b>"
        elif metric == MetricType.JITTER:
            return f"<b>{(cell.jitter_millisec.value):.2f} ms</b>"
        else:
            return f"<b>{cell.packet_loss_percent.value:.1f}%</b>"

    @staticmethod
    def make_hover_text(mesh: MeshResults) -> List[List[str]]:
        text = []
        for row in reversed(mesh.rows):
            text_col = []
            for col in row.columns:
                from_agent = mesh.agents.get_by_id(row.agent_id)
                to_agent = mesh.agents.get_by_id(col.agent_id)
                conn = mesh.connection(from_agent.id, to_agent.id)
                latency_ms = conn.latency_millisec.value
                jitter_ms = conn.jitter_millisec.value
                loss = conn.packet_loss_percent.value
                distance_km = calc_distance_in_kilometers(from_agent.coords, to_agent.coords)
                text_col.append(
                    f"{from_agent.alias} -> {to_agent.alias} <br>"
                    + f"Distance: {distance_km:.0f} km<br>"
                    + f"Latency: {latency_ms:.2f} ms <br>"
                    + f"Jitter: {jitter_ms:.2f} ms <br>"
                    + f"Loss: {loss:.1f}%"
                )
            text.append(text_col)
        for i in range(len(mesh.rows)):
            text[-(i + 1)].insert(i, "")

        return text

    @staticmethod
    def get_color(val: float, warning_threshold: Threshold, error_threshold: Threshold) -> float:
        if val < warning_threshold:
            return 0
        if val < error_threshold:
            return 0.5
        else:
            return 1.0

    @staticmethod
    def get_colorscale(z: List[List]) -> List[List]:
        RED = "rgb(255,0,0)"
        ORANGE = "rgb(255,165,0)"
        GREEN = "rgb(0,255,0)"

        if all([i == 0.0 for i in itertools.chain(*z)]):
            return [[0.0, GREEN], [1.0, GREEN]]
        if all([i == 0.5 for i in itertools.chain(*z)]):
            return [[0.0, ORANGE], [1.0, ORANGE]]
        if all([i == 1.0 for i in itertools.chain(*z)]):
            return [[0.0, RED], [1.0, RED]]
        if not any([i == 0.0 for i in itertools.chain(*z)]):
            return [[0.0, ORANGE], [1.0, RED]]
        if not any([i == 1.0 for i in itertools.chain(*z)]):
            return [[0.0, GREEN], [1.0, ORANGE]]
        else:
            return [[0.0, GREEN], [0.5, ORANGE], [1.0, RED]]
