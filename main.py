import logging
import os
import sys
from typing import Tuple

import dash
import dash_html_components as html
import flask
from dash.dependencies import Input, Output

from domain.cached_repo_request_driven import CachedRepoRequestDriven
from domain.model import MeshResults
from infrastructure.config import ConfigYAML
from infrastructure.data_access.http.synthetics_repo import SyntheticsRepo
from presentation.main_view import make_page_layout
from presentation.matrix_view import make_mesh_test_matrix_layout

FORMAT = "[%(asctime)-15s] [%(process)d] [%(levelname)s]  %(message)s"
logging.basicConfig(level=logging.INFO, format=FORMAT)
logger = logging.getLogger(__name__)


class WebApp:
    def __init__(self) -> None:
        try:
            config = ConfigYAML("data/config.yaml")
            email, token = WebApp._get_auth_email_token()
            repo = SyntheticsRepo(email, token)
            self._cached_repo = CachedRepoRequestDriven(
                repo,
                config.test_id,
                config.data_update_period_seconds,
                config.data_update_lookback_seconds,
            )
            self._config = config
            app = dash.Dash(__name__)
            app.layout = self._make_layout  # assign a method to recreate layout on every page refresh
            self._app = app

            @app.callback(Output("matrix", "figure"), [Input("metric-selector", "value")])
            def update_matrix(value):
                return make_mesh_test_matrix_layout(self.mesh, value, self.config)

        except Exception as err:
            logger.exception("WebApp initialization failure")
            sys.exit(1)

    def get_production_server(self) -> flask.Flask:
        return self._app.server

    def run_development_server(self) -> None:
        self._app.run_server(debug=True)

    def _make_layout(self) -> html.Div:
        mesh_test_results = self._cached_repo.get_mesh_test_results()
        results_timestamp = self._cached_repo.data_timestamp()
        config = self._config
        return make_page_layout(mesh_test_results, results_timestamp, config)

    @property
    def mesh(self) -> MeshResults:
        return self._cached_repo.get_mesh_test_results()

    @property
    def config(self) -> ConfigYAML:
        return self._config

    @property
    def callback(self):
        return self._app.callback

    @staticmethod
    def _get_auth_email_token() -> Tuple[str, str]:
        try:
            email = os.environ["KTAPI_AUTH_EMAIL"]
            token = os.environ["KTAPI_AUTH_TOKEN"]
            return email, token
        except KeyError:
            raise Exception("You have to specify KTAPI_AUTH_EMAIL and KTAPI_AUTH_TOKEN environment variables first")


# Run production server: gunicorn --workers=1 'main:run()'
def run() -> flask.Flask:
    app = WebApp()
    return app.get_production_server()


# Run development server: python main.py
if __name__ == "__main__":
    app = WebApp()
    app.run_development_server()
