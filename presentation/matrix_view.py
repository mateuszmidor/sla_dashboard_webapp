from typing import Dict, List

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import numpy as np
from dash.dependencies import Input, Output

from domain.config import Config
from domain.config.thresholds import Thresholds
from domain.model import MeshResults
from presentation.matrix import Matrix

RED = "rgb(255,0,0)"
ORANGE = "rgb(255,165,0)"
GREEN = "rgb(0,255,0)"


def make_mesh_test_matrix_layout(mesh: MeshResults, config: Config) -> dcc.Graph:
    matrix = Matrix(mesh)
    data = make_data(mesh, matrix, config.latency_deteriorated_ms, config.latency_failed_ms)
    annotations = make_annotations(mesh, matrix)
    layout = dict(
        margin=dict(l=150, b=50, t=100, r=50),
        modebar={"orientation": "v"},
        annotations=annotations,
        xaxis=dict(side="top", ticks="", scaleanchor="y"),
        yaxis=dict(side="left", ticks=""),
        hovermode="closest",
        showlegend=False,
    )

    return dcc.Graph(figure={"data": data, "layout": layout}, style={"width": 750, "height": 750})


def make_data(mesh: MeshResults, matrix: Matrix, latency_deteriorated_ms: int, latency_failed_ms: int) -> List[Dict]:
    x = matrix.agents
    y = [i for i in reversed(matrix.agents)]
    z = []

    for row in reversed(mesh.rows):
        z_col = []
        for col in row.columns:
            color = get_color(
                matrix.cells[row.alias][col.alias].latency_microsec.value, latency_deteriorated_ms, latency_failed_ms
            )
            z_col.append(color)
        z.append(z_col)
    for i in range(len(mesh.rows)):
        z[-(i + 1)].insert(i, None)
    z = np.array(z)

    colorscale = get_colorscale(z)

    data = [
        dict(
            x=x,
            y=y,
            z=z,
            text=make_hover_text(mesh, matrix),
            type="heatmap",
            hoverinfo="text",
            opacity=1,
            name="",
            showscale=False,
            colorscale=colorscale,
        )
    ]

    return data


def make_annotations(mesh: MeshResults, matrix: Matrix) -> List[Dict]:
    annotations = []
    for row in reversed(mesh.rows):
        for col in row.columns:
            annotations.append(
                dict(
                    showarrow=False,
                    text=f"<b>{(matrix.cells[row.alias][col.alias].latency_microsec.value * 1e-3):.2f} ms<b>",
                    xref="x",
                    yref="y",
                    x=col.alias,
                    y=row.alias,
                )
            )
    return annotations


def make_hover_text(mesh: MeshResults, matrix: Matrix) -> List[List[str]]:
    text = []
    for row in reversed(mesh.rows):
        text_col = []
        for col in row.columns:
            latency_ms = matrix.cells[row.alias][col.alias].latency_microsec.value * 1e-3
            jitter = matrix.cells[row.alias][col.alias].jitter.value
            loss = matrix.cells[row.alias][col.alias].packet_loss.value
            text_col.append(f"Latency: {latency_ms:.2f} ms, \nJiter: {jitter}, \nLoss: {loss}")
        text.append(text_col)
    for i in range(len(mesh.rows)):
        text[-(i + 1)].insert(i, "")

    return text


def get_color(val: int, latency_deteriorated_ms: int, latency_failed_ms: int):
    if val < latency_deteriorated_ms * 1000:
        return 0
    if val < latency_failed_ms * 1000:
        return 0.5
    else:
        return 1.0


def get_colorscale(z: np.array) -> List[List]:
    if np.all(z == 0.0):
        return [[0.0, GREEN], [1.0, GREEN]]
    if np.all(z == 0.5):
        return [[0.0, ORANGE], [1.0, ORANGE]]
    if np.all(z == 1.0):
        return [[0.0, RED], [1.0, RED]]
    if not np.any(z == 0.0):
        return [[0.0, ORANGE], [1.0, RED]]
    if not np.any(z == 1.0):
        return [[0.0, GREEN], [1.0, ORANGE]]
    else:
        return [[0.0, GREEN], [0.5, ORANGE], [1.0, RED]]
