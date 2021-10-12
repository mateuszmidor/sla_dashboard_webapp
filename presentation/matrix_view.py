import math
from dataclasses import dataclass, field
from typing import List, Optional
from urllib.parse import quote

from dash import dcc, html
from dash.html.Div import Div

import routing

from domain.config import Config
from domain.config.thresholds import Thresholds
from domain.geo import calc_distance
from domain.metric import MetricType, MetricValue
from domain.model import MeshResults
from domain.model.mesh_config import MeshConfig
from domain.model.mesh_results import Agent, HealthItem
from domain.types import MatrixCellColor, Threshold


@dataclass
class ToolTip:
    key: str
    value: str


@dataclass
class MatrixCell:
    text: str = ""
    href: str = ""
    color: MatrixCellColor = "rgb(0, 0, 0)"
    tooltip: List[ToolTip] = field(default_factory=list)


def tabular_tooltip(items: List[ToolTip]) -> html.Table:
    def key(s: str) -> html.Td:
        return html.Td(className="tooltip-table-key", children=s)

    def value(s: str) -> html.Td:
        return html.Td(className="tooltip-table-value", children=s)

    rows = [html.Tr([key(item.key), value(item.value)]) for item in items]
    return html.Table(children=html.Tbody(rows))


def make_tooltip_window(tooltip: List[ToolTip], href: str) -> html.Span:
    tooltip_overlay = html.Div(className="tooltip-overlay")
    tooltip_a = html.A(children=tooltip_overlay, href=href)
    return html.Span(className="tooltip-window", children=[tabular_tooltip(tooltip), tooltip_a])


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
    AUTO_REFRESH_CHECKBOX = "auto-refresh"

    def __init__(self, config: Config) -> None:
        self._config = config

    def make_layout(
        self, results: MeshResults, config: MeshConfig, data_history_seconds: int, metric: MetricType
    ) -> html.Div:

        header = self.make_header_content(results, metric, config.update_period_seconds)
        if results.connection_matrix.num_connections_with_data() > 0:
            content = self.make_matrix_content(results, config, metric)
        else:
            content = self.make_no_data_content(data_history_seconds)

        return html.Div(
            children=[
                html.Div(children=header, className="main_header"),
                html.Div(children=content, className="main_container"),
            ],
        )

    def make_header_content(self, results: MeshResults, metric: MetricType, update_period_seconds: int) -> List:
        timestamp_low_iso = results.utc_timestamp_oldest.isoformat() if results.utc_timestamp_oldest else None
        timestamp_high_iso = results.utc_timestamp_newest.isoformat() if results.utc_timestamp_newest else None
        title = html.Div(children=html.Span(children="SLA Dashboard"), className="header_title")

        if results.connection_matrix.num_connections_with_data() == 0:
            return [title]
        else:
            return [
                title,
                # Metric dropdown
                html.Div(
                    children=[
                        dcc.Dropdown(
                            id=self.METRIC_SELECTOR,
                            options=[{"label": f"{m.value} [{m.unit}]", "value": m.value} for m in MetricType],
                            value=metric.value,
                            clearable=False,
                            searchable=False,
                            className="dropdowns",
                        ),
                    ],
                    className="metric_selector",
                ),
                # Auto-refresh checkbox
                html.Div(
                    title=f"refresh page every {update_period_seconds} seconds",
                    children=[
                        dcc.Checklist(
                            id=self.AUTO_REFRESH_CHECKBOX,
                            options=[{"label": "auto-refresh", "value": "auto-refresh"}],
                            value=[],
                            persistence=True,
                            persistence_type="session",
                        ),
                        html.Span(
                            id="auto-refresh-interval-seconds",
                            title=str(update_period_seconds),  # used in client-side JS code
                        ),
                    ],
                    className="auto_refresh",
                ),
                # Time range bar
                html.Div(
                    children=[
                        html.Span("Time range: "),
                        html.Span(
                            className="header-timestamp",
                            id="timestamp-low",
                            title=timestamp_low_iso,  # used in client-side JS code
                        ),
                        html.Span(" - ", className="header-timestamp"),
                        html.Span(
                            className="header-timestamp",
                            id="timestamp-high",
                            title=timestamp_high_iso,  # used in client-side JS code
                        ),
                    ],
                    className="time_range",
                ),
            ]

    def make_matrix_content(self, results: MeshResults, config: MeshConfig, metric: MetricType) -> List:
        matrix_table = self._make_matrix_table(results, config, metric)
        return [html.Div(className="scrollbox", children=matrix_table)]

    # noinspection PyMethodMayBeStatic
    def make_no_data_content(self, data_history_seconds: int) -> List:
        no_data = f"No test results available for the last {int(data_history_seconds)} seconds"
        return [html.H1(no_data), html.Br(), html.Br()]

    # noinspection PyPep8Naming
    def _make_matrix_table(self, results: MeshResults, config: MeshConfig, metric_type: MetricType) -> html.Table:
        matrix_rows = self._make_matrix_rows(results, config, metric_type)
        html_rows = []
        for n_row, row in enumerate(matrix_rows):
            html_row = []
            for n_col, cell in enumerate(row):
                if n_row == n_col:
                    className = "diagonal-cell"
                elif n_row == 0:
                    className = "to-agent-cell"
                elif n_col == 0:
                    className = "from-agent-cell"
                else:
                    className = "measurement-cell"

                if cell.tooltip and cell.href:
                    # measurement cell
                    cell_text = cell.text if self._config.show_measurement_values else html.Br()
                    cell_overlay = html.Div(className="cell-overlay", children=cell_text)
                    cell_contents = html.A(className="cell-measurement", children=cell_overlay, href=cell.href)

                    tooltip_window = make_tooltip_window(cell.tooltip, cell.href)

                    contents_tooltip = html.Div(className="tooltip-container", children=[cell_contents, tooltip_window])
                    cell_style = {"background-color": cell.color}
                    cell = html.Td(className=className, style=cell_style, children=contents_tooltip)
                else:
                    # header/diagonal cell
                    children = self._make_legend() if n_col == 0 and n_row == 0 else cell.text
                    cell = html.Td(className=className, children=children)

                html_row.append(cell)
            html_rows.append(html.Tr(className="connection-matrix-row", children=html_row))
        return html.Table(className="connection-matrix", children=html.Tbody(html_rows))

    def _make_matrix_rows(
        self, results: MeshResults, config: MeshConfig, metric_type: MetricType
    ) -> List[List[MatrixCell]]:
        rows: List[List[MatrixCell]] = []

        header = [MatrixCell()] + [MatrixCell(text=self._agent_label(a)) for a in config.agents.all()]
        rows.append(header)

        thresholds = self._get_thresholds(metric_type)
        for from_agent in config.agents.all():
            row: List[MatrixCell] = [MatrixCell(text=self._agent_label(from_agent))]
            for to_agent in config.agents.all():
                if from_agent == to_agent:
                    row.append(MatrixCell())  # matrix diagonal
                else:
                    warning = thresholds.warning(from_agent.id, to_agent.id)
                    critical = thresholds.critical(from_agent.id, to_agent.id)
                    health = results.connection(from_agent.id, to_agent.id).latest_measurement
                    tooltip = self._make_tooltip_items(from_agent, to_agent, results)
                    href = quote(routing.encode_time_series_path(from_agent.id, to_agent.id))
                    if health:
                        metric = health.get_metric(metric_type)
                        color = self._cell_color(metric.value, warning, critical)
                        text = format_health(metric_type, health)
                        row.append(MatrixCell(text=text, tooltip=tooltip, color=color, href=href))
                    else:
                        color_nodata = self._config.matrix.cell_color_nodata
                        row.append(MatrixCell(text="-", tooltip=tooltip, color=color_nodata, href=href))
            rows.append(row)
        return rows

    def _cell_color(self, val: MetricValue, warning: Threshold, critical: Threshold) -> MatrixCellColor:
        config = self._config.matrix
        if math.isnan(val):
            return config.cell_color_nodata
        if val >= critical:
            return config.cell_color_critical
        if val >= warning:
            return config.cell_color_warning
        return config.cell_color_healthy

    def _get_thresholds(self, metric: MetricType) -> Thresholds:
        if metric == MetricType.LATENCY:
            return self._config.latency
        if metric == MetricType.JITTER:
            return self._config.jitter
        return self._config.packet_loss

    def _make_tooltip_items(self, from_agent: Agent, to_agent: Agent, mesh: MeshResults) -> List[ToolTip]:
        if from_agent == to_agent:
            return []
        conn = mesh.connection(from_agent.id, to_agent.id)
        distance_unit = self._config.distance_unit
        distance = calc_distance(from_agent.coords, to_agent.coords, distance_unit)

        items: List[ToolTip] = [
            ToolTip("From", f"{from_agent.name}, {from_agent.alias} [{from_agent.id}]"),
            ToolTip("To", f" {to_agent.name}, {to_agent.alias} [{to_agent.id}]"),
            ToolTip("Distance", f"{distance:.0f} {distance_unit.value}"),
        ]

        health = conn.latest_measurement
        if health:
            for m in MetricType:
                items.append(ToolTip(m.value, f"{format_health(m, health, True)}"))
            items.append(ToolTip("Timestamp", f"{health.timestamp.strftime('%x %X %Z')}"))
        else:
            # no data available for this connection
            pass

        return items

    def _agent_label(self, agent: Agent) -> str:
        return self._config.agent_label.format(name=agent.name, alias=agent.alias, id=agent.id, ip=agent.ip)

    def _make_legend(self) -> html.Div:
        return html.Div(
            children=[
                html.Label("Healthy", className="chart_legend__label chart_legend__label_healthy"),
                html.Div(
                    className="chart_legend__cell",
                    style={"background": self._config.matrix.cell_color_healthy},
                ),
                html.Span(className="chart_legend__separator"),
                html.Label("Warning", className="chart_legend__label chart_legend__label_warning"),
                html.Div(
                    className="chart_legend__cell",
                    style={"background": self._config.matrix.cell_color_warning},
                ),
                html.Span(className="chart_legend__separator"),
                html.Label("Critical", className="chart_legend__label chart_legend__label_critical"),
                html.Div(
                    className="chart_legend__cell",
                    style={"background": self._config.matrix.cell_color_critical},
                ),
                html.Span(className="chart_legend__separator"),
                html.Label("No data", className="chart_legend__label chart_legend__label_nodata"),
                html.Div(
                    className="chart_legend__cell",
                    style={"background": self._config.matrix.cell_color_nodata},
                ),
            ],
            className="chart_legend",
        )
