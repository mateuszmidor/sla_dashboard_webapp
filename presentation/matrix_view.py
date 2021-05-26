import itertools
from typing import Dict, List

from domain.config import Config
from domain.config.thresholds import Thresholds
from domain.model import MeshResults
from domain.model.mesh_results import MeshColumn, Metric
from presentation.matrix import Matrix

RED = "rgb(255,0,0)"
ORANGE = "rgb(255,165,0)"
GREEN = "rgb(0,255,0)"


def make_mesh_test_matrix_layout(mesh: MeshResults, metric: str, config: Config) -> Dict:
    matrix = Matrix(mesh)
    data = make_data(mesh, metric, matrix, get_tresholds(metric, config))
    annotations = make_annotations(mesh, metric, matrix)
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


def get_tresholds(metric: str, config: Config) -> Thresholds:
    if metric == "latency":
        return config.latency
    elif metric == "jitter":
        return config.jitter
    else:
        return config.packet_loss


def make_data(mesh: MeshResults, metric: str, matrix: Matrix, tresholds: Thresholds) -> List[Dict]:
    colors = make_colors(mesh, metric, matrix, tresholds)
    return [
        dict(
            x=matrix.agents,
            y=[i for i in reversed(matrix.agents)],
            z=colors,
            text=make_hover_text(mesh, matrix),
            type="heatmap",
            hoverinfo="text",
            opacity=1,
            name="",
            showscale=False,
            colorscale=get_colorscale(colors),
        )
    ]


def make_colors(mesh: MeshResults, metric: str, matrix: Matrix, tresholds: Thresholds) -> List[List]:
    colors = []
    for row in reversed(mesh.rows):
        colors_col = []
        for col in row.columns:
            deteriorated = tresholds.deteriorated(row.agent_id, col.agent_id)
            failed = tresholds.failed(row.agent_id, col.agent_id)
            value = get_metric_value(metric, matrix.cells[row.agent_alias][col.agent_alias])
            color = get_color(value, deteriorated, failed)
            colors_col.append(color)
        colors.append(colors_col)

    for i in range(len(mesh.rows)):  # add Nones at diagonal to avoid colorising it
        colors[-(i + 1)].insert(i, None)  # type: ignore

    return colors


def get_metric_value(metric: str, cell: MeshColumn) -> int:
    if metric == "latency":
        return cell.latency_microsec.value
    elif metric == "jitter":
        return cell.jitter_microsec.value
    else:
        return cell.packet_loss_percent.value


def make_annotations(mesh: MeshResults, metric: str, matrix: Matrix) -> List[Dict]:
    annotations = []
    for row in reversed(mesh.rows):
        for col in row.columns:
            text = get_text(metric, matrix.cells[row.agent_alias][col.agent_alias])
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


def get_text(metric: str, cell: MeshColumn) -> str:
    if metric == "latency":
        return f"<b>{(cell.latency_microsec.value * 1e-3):.2f} ms</b>"
    elif metric == "jitter":
        return f"<b>{(cell.jitter_microsec.value * 1e-3):.2f} ms</b>"
    else:
        return f"<b>{cell.packet_loss_percent.value:.1f}%</b>"


def make_hover_text(mesh: MeshResults, matrix: Matrix) -> List[List[str]]:
    text = []
    for row in reversed(mesh.rows):
        text_col = []
        for col in row.columns:

            latency_ms = matrix.cells[row.agent_alias][col.agent_alias].latency_microsec.value * 1e-3
            jitter_ms = matrix.cells[row.agent_alias][col.agent_alias].jitter_microsec.value * 1e-3
            loss = matrix.cells[row.agent_alias][col.agent_alias].packet_loss_percent.value
            text_col.append(
                f"{row.agent_alias} -> {col.agent_alias} <br>Latency: {latency_ms:.2f} ms, <br>Jitter: {jitter_ms:.2f} ms, <br>Loss: {loss:.1f}%"
            )
        text.append(text_col)
    for i in range(len(mesh.rows)):
        text[-(i + 1)].insert(i, "")

    return text


def get_color(val: int, latency_deteriorated_us: int, latency_failed_us: int) -> float:
    if val < latency_deteriorated_us:
        return 0
    if val < latency_failed_us:
        return 0.5
    else:
        return 1.0


def get_colorscale(z: List[List]) -> List[List]:
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
