import logging
import os
import sys
from typing import Any, Dict, Optional, Tuple

import dash
import dash_core_components as dcc
import dash_html_components as html
import flask
from dash.dependencies import Input, Output

from domain.cached_repo_request_driven import CachedRepoRequestDriven
from domain.metric import Metric
from domain.model import MeshResults
from domain.types import AgentID
from infrastructure.config import ConfigYAML
from infrastructure.data_access.http.synthetics_repo import SyntheticsRepo
from presentation.chart_view import ChartView
from presentation.http_error_view import HTTPErrorView
from presentation.index_view import IndexView
from presentation.matrix_view import MatrixView

FORMAT = "[%(asctime)-15s] [%(process)d] [%(levelname)s]  %(message)s"
logging.basicConfig(level=logging.INFO, format=FORMAT)
logger = logging.getLogger(__name__)


class WebApp:
    def __init__(self) -> None:
        try:
            config = ConfigYAML("data/config.yaml")
            email, token = get_auth_email_token()
            repo = SyntheticsRepo(email, token)
            self._cached_repo = CachedRepoRequestDriven(
                repo,
                config.test_id,
                config.data_update_period_seconds,
                config.data_update_lookback_seconds,
            )
            self._config = config
            app = dash.Dash(__name__, suppress_callback_exceptions=True)
            app.layout = IndexView.make_layout()
            self._app = app
            self._current_metric = Metric.LATENCY

            # all views - handle path change
            @app.callback(Output(IndexView.PAGE_CONTENT, "children"), [Input(IndexView.URL, "pathname")])
            def display_page(pathname: str):
                return self._get_page_content(pathname)

            # matrix view - handle metric select
            @app.callback(Output(MatrixView.MATRIX, "figure"), [Input(MatrixView.METRIC_SELECTOR, "value")])
            def update_matrix(value: str):
                metric = Metric(value)
                self._current_metric = metric
                return MatrixView.make_matrix_data(self.mesh, metric, self.config)

            # matrix view - handle cell click
            @app.callback(Output(IndexView.REDIRECT, "children"), Input(MatrixView.MATRIX, "clickData"))
            def open_chart(clickData: Optional[Dict[str, Any]]):
                if clickData is not None:
                    return self._handle_cell_click(clickData["points"][0]["x"], clickData["points"][0]["y"])

        except Exception as err:
            logger.exception("WebApp initialization failure")
            sys.exit(1)

    def get_production_server(self) -> flask.Flask:
        return self._app.server

    def run_development_server(self) -> None:
        self._app.run_server(debug=True)

    def _get_page_content(self, pathname: str) -> html.Div:
        try:
            if pathname == "/":
                return self._make_matrix_layout()
            elif pathname.startswith("/chart"):
                return self._make_chart_layout(pathname)
            else:
                return HTTPErrorView.make_layout(404)
        except Exception as err:
            logger.exception("Error while rendering page")
            return HTTPErrorView.make_layout(500)

    def _handle_cell_click(self, x, y: str) -> Optional[dcc.Location]:
        from_agent_alias, to_agent_alias = y, x
        if from_agent_alias == to_agent_alias:
            return None

        results = self._cached_repo.get_mesh_test_results()
        from_agent_id = results.agents.get_id(from_agent_alias)
        to_agent_id = results.agents.get_id(to_agent_alias)

        return self._redirect_to_chart_view(from_agent_id, to_agent_id, self._current_metric)

    def _make_matrix_layout(self) -> html.Div:
        mesh_test_results = self._cached_repo.get_mesh_test_results()
        results_timestamp = self._cached_repo.data_timestamp()
        metric = self._current_metric
        return MatrixView.make_layout(mesh_test_results, results_timestamp, metric)

    def _make_chart_layout(self, path: str) -> html.Div:
        from_agent, to_agent, metric = ChartView.decode_path(path)
        results = self._cached_repo.get_mesh_test_results()
        return ChartView.make_layout(from_agent, to_agent, metric, results)

    @staticmethod
    def _redirect_to_chart_view(from_agent, to_agent: AgentID, metric: Metric) -> dcc.Location:
        path = ChartView.encode_path(from_agent, to_agent, metric)
        return dcc.Location(pathname=path, id="")

    @property
    def mesh(self) -> MeshResults:
        return self._cached_repo.get_mesh_test_results()

    @property
    def config(self) -> ConfigYAML:
        return self._config

    @property
    def callback(self):
        return self._app.callback


def get_auth_email_token() -> Tuple[str, str]:
    try:
        return os.environ["KTAPI_AUTH_EMAIL"], os.environ["KTAPI_AUTH_TOKEN"]
    except KeyError as err:
        raise Exception(f"{err} environment variable is missing")


# Run production server: gunicorn --workers=1 'main:run()'
def run() -> flask.Flask:
    app = WebApp()
    return app.get_production_server()


# Run development server: python main.py
if __name__ == "__main__":
    app = WebApp()
    app.run_development_server()
