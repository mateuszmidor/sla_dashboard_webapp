import itertools
from datetime import datetime
from os import stat
from typing import Dict, List

import dash_core_components as dcc
import dash_html_components as html

from domain.config import Config
from domain.config.thresholds import Thresholds
from domain.metric import Metric
from domain.model import MeshResults
from domain.model.mesh_results import MeshColumn
from domain.types import MetricValue, Threshold
from presentation.localtime import utc_to_localtime
from presentation.matrix import Matrix


class MatrixView:
    MATRIX = "matrix"
    METRIC_SELECTOR = "metric-selector"

    @staticmethod
    def make_layout(mesh: MeshResults, metric: Metric) -> html.Div:
        localtime_timestamp = utc_to_localtime(mesh.utc_timestamp)
        timestamp = localtime_timestamp.strftime("%H:%M:%S")
        header = "SLA Dashboard"
        return html.Div(
            children=[
                html.H1(children=header, style={"textAlign": "center", "marginBottom": 50}),
                html.H2(
                    f"Data timestamp {timestamp}",
                    style={"textAlign": "center", "marginTop": 100},
                ),
                html.Center("Select primary metric: "),
                dcc.Dropdown(
                    id=MatrixView.METRIC_SELECTOR,
                    options=[
                        {"label": "Latency [ms]", "value": Metric.LATENCY.value},
                        {"label": "Jitter [ms]", "value": Metric.JITTER.value},
                        {"label": "Packet loss [%]", "value": Metric.PACKET_LOSS.value},
                    ],
                    value=metric.value,
                    clearable=False,
                    style={"width": 450, "margin-left": "auto", "margin-right": "auto"},
                ),
                html.Div(
                    html.Center(
                        dcc.Graph(id=MatrixView.MATRIX, style={"width": 750, "height": 750}),
                        style={"marginLeft": 200, "marginRight": 200},
                    ),
                ),
            ],
            style={"marginBottom": 50, "marginTop": 50, "marginLeft": 50, "marginRight": 50},
        )

    @staticmethod
    def make_matrix_data(mesh: MeshResults, metric: Metric, config: Config) -> Dict:
        matrix = Matrix(mesh)
        data = MatrixView.make_data(mesh, metric, matrix, MatrixView.get_tresholds(metric, config))
        annotations = MatrixView.make_annotations(mesh, metric, matrix)
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
    def get_tresholds(metric: Metric, config: Config) -> Thresholds:
        if metric == Metric.LATENCY:
            return config.latency
        elif metric == Metric.JITTER:
            return config.jitter
        else:
            return config.packet_loss

    @staticmethod
    def make_data(mesh: MeshResults, metric: Metric, matrix: Matrix, tresholds: Thresholds) -> List[Dict]:
        colors = MatrixView.make_colors(mesh, metric, matrix, tresholds)
        return [
            dict(
                x=matrix.agents,
                y=[i for i in reversed(matrix.agents)],
                z=colors,
                text=MatrixView.make_hover_text(mesh, matrix),
                type="heatmap",
                hoverinfo="text",
                opacity=1,
                name="",
                showscale=False,
                colorscale=MatrixView.get_colorscale(colors),
            )
        ]

    @staticmethod
    def make_colors(mesh: MeshResults, metric: Metric, matrix: Matrix, tresholds: Thresholds) -> List[List]:
        colors = []
        for row in reversed(mesh.rows):
            colors_col = []
            for col in row.columns:
                warning = tresholds.warning(row.agent_id, col.agent_id)
                error = tresholds.error(row.agent_id, col.agent_id)
                value = MatrixView.get_metric_value(metric, matrix.cells[row.agent_alias][col.agent_alias])
                color = MatrixView.get_color(value, warning, error)
                colors_col.append(color)
            colors.append(colors_col)

        for i in range(len(mesh.rows)):  # add Nones at diagonal to avoid colorising it
            colors[-(i + 1)].insert(i, None)  # type: ignore

        return colors

    @staticmethod
    def get_metric_value(metric: Metric, cell: MeshColumn) -> MetricValue:
        if metric == Metric.LATENCY:
            return cell.latency_millisec.value
        elif metric == Metric.JITTER:
            return cell.jitter_millisec.value
        else:
            return cell.packet_loss_percent.value

    @staticmethod
    def make_annotations(mesh: MeshResults, metric: Metric, matrix: Matrix) -> List[Dict]:
        annotations = []
        for row in reversed(mesh.rows):
            for col in row.columns:
                text = MatrixView.get_text(metric, matrix.cells[row.agent_alias][col.agent_alias])
                annotations.append(
                    dict(
                        showarrow=False,
                        text=text,
                        xref="x",
                        yref="y",
                        x=col.agent_alias,
                        y=row.agent_alias,
                    )
                )
        return annotations

    @staticmethod
    def get_text(metric: Metric, cell: MeshColumn) -> str:
        if metric == Metric.LATENCY:
            return f"<b>{(cell.latency_millisec.value):.2f} ms</b>"
        elif metric == Metric.JITTER:
            return f"<b>{(cell.jitter_millisec.value):.2f} ms</b>"
        else:
            return f"<b>{cell.packet_loss_percent.value:.1f}%</b>"

    @staticmethod
    def make_hover_text(mesh: MeshResults, matrix: Matrix) -> List[List[str]]:
        text = []
        for row in reversed(mesh.rows):
            text_col = []
            for col in row.columns:

                latency_ms = matrix.cells[row.agent_alias][col.agent_alias].latency_millisec.value
                jitter_ms = matrix.cells[row.agent_alias][col.agent_alias].jitter_millisec.value
                loss = matrix.cells[row.agent_alias][col.agent_alias].packet_loss_percent.value
                text_col.append(
                    f"{row.agent_alias} -> {col.agent_alias} <br>Latency: {latency_ms:.2f} ms, <br>Jitter: {jitter_ms:.2f} ms, <br>Loss: {loss:.1f}%"
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
