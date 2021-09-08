import logging
import math
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import dash_core_components as dcc
import dash_html_components as html
from dash_dangerously_set_inner_html import DangerouslySetInnerHTML
from jinja2 import Environment, FileSystemLoader

from domain.config import Config
from domain.config.thresholds import Thresholds
from domain.geo import calc_distance
from domain.metric import MetricType, MetricValue
from domain.model import MeshResults
from domain.model.mesh_config import MeshConfig
from domain.model.mesh_results import Agent, Agents, HealthItem
from domain.types import AgentID, Threshold


class CellTag(str, Enum):
    """This type is input to matrix_view.j2"""

    HEALTHY = "td-healthy"
    WARNING = "td-warning"
    CRITICAL = "td-critical"
    NODATA = "td-nodata"
    NONE = ""


@dataclass
class MatrixCell:
    """This type is input to matrix_view.j2"""

    text: str = ""
    tooltip: str = ""
    tag: str = CellTag.NONE.value


@dataclass
class MatrixData:
    """This type is input to matrix_view.j2"""

    rows: List[List[MatrixCell]]


def agent_label(agent: Agent) -> str:
    return agent.name


class MatrixView:
    MATRIX = "matrix"
    METRIC_SELECTOR = "metric-selector"

    def __init__(self, config: Config) -> None:
        self._config = config
        self._agents = Agents()
        file_loader = FileSystemLoader("data/templates")
        env = Environment(loader=file_loader)
        self._template = env.get_template("matrix_view.j2")

    def make_layout(
        self, results: MeshResults, config: MeshConfig, data_history_seconds: int, metric: MetricType
    ) -> html.Div:
        title = "SLA Dashboard"
        if results.connection_matrix.num_connections_with_data() > 0:
            content = self.make_matrix_content(results, config, metric)
        else:
            content = self.make_no_data_content(data_history_seconds)

        return html.Div(
            children=[
                html.H1(children=title, className="header_main"),
                html.Div(children=content, className="main_container"),
            ]
        )

    def make_matrix_content(self, results: MeshResults, config: MeshConfig, metric: MetricType) -> List:
        self._agents = config.agents  # remember agents used to make the layout for further processing
        timestamp_low_iso = results.utc_timestamp_oldest.isoformat() if results.utc_timestamp_oldest else None
        timestamp_high_iso = results.utc_timestamp_newest.isoformat() if results.utc_timestamp_newest else None
        matrix_html = self._make_matrix_html(results, config, metric)
        return [
            html.H2(
                children=[
                    html.Span("Time range: "),
                    html.Span(
                        "<test_results_timestamp_low>",
                        className="header-timestamp",
                        id="timestamp-low",
                        title=timestamp_low_iso,
                    ),
                    html.Span(" - ", className="header-timestamp"),
                    html.Span(
                        "<test_results_timestamp_high>",
                        className="header-timestamp",
                        id="timestamp-high",
                        title=timestamp_high_iso,
                    ),
                ],
                className="header__subTitle",
            ),
            html.Div(
                children=[
                    html.Label("Select primary metric:", className="select_label"),
                    dcc.Dropdown(
                        id=self.METRIC_SELECTOR,
                        options=[{"label": f"{m.value} [{m.unit}]", "value": m.value} for m in MetricType],
                        value=metric.value,
                        clearable=False,
                        className="dropdowns",
                    ),
                ],
                className="select_container",
            ),
            html.Div(
                children=[
                    html.Div([DangerouslySetInnerHTML(matrix_html)]),  # render actual matrix here
                    html.Div(
                        children=[
                            html.Label("Healthy", className="chart_legend__label chart_legend__label_healthy"),
                            html.Div(
                                className="chart_legend__cell",
                                style={"background": self._config.matrix.cell_color_healthy},
                            ),
                            html.Label("Warning", className="chart_legend__label chart_legend__label_warning"),
                            html.Div(
                                className="chart_legend__cell",
                                style={"background": self._config.matrix.cell_color_warning},
                            ),
                            html.Label("Critical", className="chart_legend__label chart_legend__label_critical"),
                            html.Div(
                                className="chart_legend__cell",
                                style={"background": self._config.matrix.cell_color_critical},
                            ),
                            html.Label("No data", className="chart_legend__label chart_legend__label_nodata"),
                            html.Div(
                                className="chart_legend__cell",
                                style={"background": self._config.matrix.cell_color_nodata},
                            ),
                        ],
                        className="chart_legend",
                    ),
                ],
            ),
        ]

    def make_no_data_content(self, data_history_seconds: int) -> List:
        no_data = f"No test results available for the last {int(data_history_seconds)} seconds"
        return [html.H1(no_data), html.Br(), html.Br()]

    def _make_matrix_html(self, results: MeshResults, config: MeshConfig, metric_type: MetricType) -> str:
        matrix_rows = self._make_matrix_rows(results, config, metric_type)
        data = MatrixData(rows=matrix_rows)
        return self._template.render(data=data, config=self._config.matrix)

    def _make_matrix_rows(
        self, results: MeshResults, config: MeshConfig, metric_type: MetricType
    ) -> List[List[MatrixCell]]:
        rows: List[List[MatrixCell]] = []

        header = [MatrixCell()] + [MatrixCell(text=agent_label(a)) for a in config.agents.all()]
        rows.append(header)

        thresholds = self.get_thresholds(metric_type)
        for from_agent in config.agents.all():
            row: List[MatrixCell] = [MatrixCell(text=agent_label(from_agent))]
            for to_agent in config.agents.all():
                if from_agent == to_agent:
                    row.append(MatrixCell())  # matrix diagonal
                else:
                    warning = thresholds.warning(from_agent.id, to_agent.id)
                    critical = thresholds.critical(from_agent.id, to_agent.id)
                    health = results.connection(from_agent.id, to_agent.id).latest_measurement
                    tooltip = self.make_tooltip_text(from_agent, to_agent, results)
                    if health:
                        metric = health.get_metric(metric_type)
                        tag = self.get_cell_tag(metric.value, warning, critical)
                        text = self.format_health(metric_type, health)
                        row.append(MatrixCell(text=text, tooltip=tooltip, tag=tag.value))
                    else:
                        row.append(MatrixCell(text="-", tooltip=tooltip, tag=CellTag.NODATA.value))
            rows.append(row)
        return rows

    def get_thresholds(self, metric: MetricType) -> Thresholds:
        if metric == MetricType.LATENCY:
            return self._config.latency
        if metric == MetricType.JITTER:
            return self._config.jitter
        return self._config.packet_loss

    @staticmethod
    def format_health(
        metric_type: MetricType, health: Optional[HealthItem], include_unit: bool = False, nan="N/A"
    ) -> str:
        if not health:
            return nan

        metric = health.get_metric(metric_type)
        if math.isnan(metric.value):
            return nan

        return "{:.2f}{}".format(metric.value, metric.unit if include_unit else "")

    def make_tooltip_text(self, from_agent: Agent, to_agent: Agent, mesh: MeshResults) -> str:
        if from_agent == to_agent:
            return ""
        conn = mesh.connection(from_agent.id, to_agent.id)
        distance_unit = self._config.distance_unit
        distance = calc_distance(from_agent.coords, to_agent.coords, distance_unit)

        tooltip_lines: List[str] = [
            f"From: {from_agent.name}, {from_agent.alias} [{from_agent.id}]",
            f"To: {to_agent.name}, {to_agent.alias} [{to_agent.id}]",
            f"Distance: {distance:.0f} {distance_unit.value}",
        ]

        health = conn.latest_measurement
        if health:
            for m in MetricType:
                tooltip_lines.append(f"{m.value}: {self.format_health(m, health, True)}")
            tooltip_lines.append(f"Time stamp: {health.timestamp.strftime('%x %X %Z')}")
            tooltip_lines.append(f"Num measurements: {len(conn.health)}")
        else:
            # no data available for this connection
            tooltip_lines.append("NO DATA")

        return "<br>".join(tooltip_lines)

    @staticmethod
    def get_cell_tag(val: MetricValue, warning_threshold: Threshold, critical_threshold: Threshold) -> CellTag:
        if math.isnan(val):
            return CellTag.NODATA
        if val < warning_threshold:
            return CellTag.HEALTHY
        if val < critical_threshold:
            return CellTag.WARNING
        return CellTag.CRITICAL

    def get_agents_from_click(
        self, click_data: Optional[Dict[str, Any]]
    ) -> Tuple[Optional[AgentID], Optional[AgentID]]:
        if click_data is None:
            return None, None

        to_agent = self._agents.get_by_name(click_data["points"][0]["x"])
        from_agent = self._agents.get_by_name(click_data["points"][0]["y"])
        logging.debug(
            "click: x: %s y: %s from: %s to: %s",
            click_data["points"][0]["x"],
            click_data["points"][0]["y"],
            from_agent.id,
            to_agent.id,
        )
        return from_agent.id, to_agent.id
