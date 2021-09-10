import math
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Union
from urllib.parse import quote

import dash_core_components as dcc
import dash_html_components as html

import routing

from domain.config import Config
from domain.config.thresholds import Thresholds
from domain.geo import calc_distance
from domain.metric import MetricType, MetricValue
from domain.model import MeshResults
from domain.model.mesh_config import MeshConfig
from domain.model.mesh_results import Agent, HealthItem
from domain.types import MatrixCellColor, Threshold


class CellTag(Enum):
    HEALTHY = 1
    WARNING = 2
    CRITICAL = 3
    NODATA = 4


@dataclass
class MatrixCell:
    text: str = ""
    href: str = ""
    tooltip: str = ""
    tag: CellTag = CellTag.NODATA


def agent_label(agent: Agent) -> str:
    return agent.alias


def dash_multiline(text: str) -> List[Union[str, html.Br]]:
    result: List[Union[str, html.Br]] = []
    for line in text.split("\n"):
        result.append(line)
        result.append(html.Br())
    return result


def cell_tag(val: MetricValue, warning_threshold: Threshold, critical_threshold: Threshold) -> CellTag:
    if math.isnan(val):
        return CellTag.NODATA
    if val < warning_threshold:
        return CellTag.HEALTHY
    if val < critical_threshold:
        return CellTag.WARNING
    return CellTag.CRITICAL


def format_health(metric_type: MetricType, health: Optional[HealthItem], include_unit: bool = False, nan="N/A") -> str:
    if not health:
        return nan

    metric = health.get_metric(metric_type)
    if math.isnan(metric.value):
        return nan

    format_str = "{:.2f}{}" if metric_type == MetricType.JITTER else "{:.0f}{}"
    return format_str.format(metric.value, metric.unit if include_unit else "")


class MatrixView:
    METRIC_SELECTOR = "metric-selector"

    def __init__(self, config: Config) -> None:
        self._config = config

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
        timestamp_low_iso = results.utc_timestamp_oldest.isoformat() if results.utc_timestamp_oldest else None
        timestamp_high_iso = results.utc_timestamp_newest.isoformat() if results.utc_timestamp_newest else None
        matrix_table = self._make_matrix_table(results, config, metric)

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
                    html.Div(className="scrollbox", children=matrix_table),
                    html.Br(),
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

    def _make_matrix_table(self, results: MeshResults, config: MeshConfig, metric_type: MetricType) -> html.Table:
        matrix_rows = self._make_matrix_rows(results, config, metric_type)
        html_rows = []
        for n_row, row in enumerate(matrix_rows):
            html_row = []
            for n_col, cell in enumerate(row):
                if n_row == n_col:
                    className = "td-diagonal"
                elif n_row == 0:
                    className = "td-agent vertical"
                elif n_col == 0:
                    className = "td-agent"
                else:
                    className = "td-data"

                if cell.tooltip != "" and cell.href != "":
                    html_a = html.A(className="a-data", children=cell.text, href=cell.href)
                    html_span = html.Span(className="tooltiptext", children=dash_multiline(cell.tooltip))
                    html_div = html.Div(className="tooltip", children=[html_a, html_span])
                    cell_color = self._tag_to_color(cell.tag)
                    html_td = html.Td(className=className, style={"background-color": cell_color}, children=html_div)
                else:
                    html_td = html.Td(className=className, children=cell.text)

                html_row.append(html_td)
            html_rows.append(html.Tr(html_row))
        return html.Table(className="connection-matrix", children=html.Tbody(html_rows))

    def _make_matrix_rows(
        self, results: MeshResults, config: MeshConfig, metric_type: MetricType
    ) -> List[List[MatrixCell]]:
        rows: List[List[MatrixCell]] = []

        header = [MatrixCell()] + [MatrixCell(text=agent_label(a)) for a in config.agents.all()]
        rows.append(header)

        thresholds = self._get_thresholds(metric_type)
        for from_agent in config.agents.all():
            row: List[MatrixCell] = [MatrixCell(text=agent_label(from_agent))]
            for to_agent in config.agents.all():
                if from_agent == to_agent:
                    row.append(MatrixCell())  # matrix diagonal
                else:
                    warning = thresholds.warning(from_agent.id, to_agent.id)
                    critical = thresholds.critical(from_agent.id, to_agent.id)
                    health = results.connection(from_agent.id, to_agent.id).latest_measurement
                    tooltip = self._make_tooltip_text(from_agent, to_agent, results)
                    href = quote(routing.encode_time_series_path(from_agent.id, to_agent.id))
                    if health:
                        metric = health.get_metric(metric_type)
                        tag = cell_tag(metric.value, warning, critical)
                        text = format_health(metric_type, health)
                        row.append(MatrixCell(text=text, tooltip=tooltip, tag=tag, href=href))
                    else:
                        row.append(MatrixCell(text="-", tooltip=tooltip, tag=CellTag.NODATA, href=href))
            rows.append(row)
        return rows

    def _tag_to_color(self, tag: CellTag) -> MatrixCellColor:
        config = self._config.matrix
        # KeyError here means programming error
        return {
            CellTag.HEALTHY: config.cell_color_healthy,
            CellTag.WARNING: config.cell_color_warning,
            CellTag.CRITICAL: config.cell_color_critical,
            CellTag.NODATA: config.cell_color_nodata,
        }[tag]

    def _get_thresholds(self, metric: MetricType) -> Thresholds:
        if metric == MetricType.LATENCY:
            return self._config.latency
        if metric == MetricType.JITTER:
            return self._config.jitter
        return self._config.packet_loss

    def _make_tooltip_text(self, from_agent: Agent, to_agent: Agent, mesh: MeshResults) -> str:
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
                tooltip_lines.append(f"{m.value}: {format_health(m, health, True)}")
            tooltip_lines.append(f"Time stamp: {health.timestamp.strftime('%x %X %Z')}")
        else:
            # no data available for this connection
            tooltip_lines.append("NO DATA")

        return "\n".join(tooltip_lines)
