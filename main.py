import logging
import os
import sys
import time
from threading import Thread
from typing import Tuple

import dash

from domain.cached_repo_request_driven import CachedRepoRequestDriven
from infrastructure.config import ConfigYAML
from infrastructure.data_access.http.synthetics_repo import SyntheticsRepo
from presentation.main_view import make_page_layout
from presentation.matrix_view import make_mesh_test_matrix_layout

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class WebApp:
    def __init__(self, email, token: str) -> None:
        try:
            config = ConfigYAML("config.yaml")
            repo = SyntheticsRepo(email, token)
            self._cached_repo = CachedRepoRequestDriven(
                repo,
                config.test_id,
                config.data_update_period_seconds,
                config.data_update_lookback_seconds,
            )
            self._config = config
        except Exception as err:
            logger.exception("WebApp initialization failure")
            sys.exit(1)

    def run(self) -> None:
        app = dash.Dash(__name__)
        app.layout = self._make_layout  # assign a method to recreate layout on every page refresh
        app.run_server(debug=True)

    def _make_layout(self):
        mesh_test_results = self._cached_repo.get_mesh_test_results()
        results_timestamp = self._cached_repo.data_timestamp()
        config = self._config
        return make_page_layout(mesh_test_results, results_timestamp, config)


def get_auth_email_token() -> Tuple[str, str]:
    try:
        email = os.environ["KTAPI_AUTH_EMAIL"]
        token = os.environ["KTAPI_AUTH_TOKEN"]
        return email, token
    except KeyError:
        print("You have to specify KTAPI_AUTH_EMAIL and KTAPI_AUTH_TOKEN first")
        sys.exit(1)


if __name__ == "__main__":
    email, token = get_auth_email_token()
    app = WebApp(email, token)
    app.run()
