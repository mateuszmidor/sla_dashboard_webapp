import logging
import os
import sys
import time
from threading import Thread
from typing import Tuple

import dash

from domain.cached_repo import CachedRepo
from infrastructure.config import ConfigYAML
from infrastructure.data_access.http.synthetics_repo import SyntheticsRepo
from presentation.main_view import make_page_layout
from presentation.matrix_view import make_mesh_test_matrix_layout

logger = logging.getLogger(__name__)


class WebApp:
    def __init__(self, email, token: str) -> None:
        try:
            repo = SyntheticsRepo(email, token)
            self._config = ConfigYAML("config.yaml")
            self._cached_repo = CachedRepo(repo, self._config.test_id)
        except Exception as err:
            logger.exception(f"WebApp initialization failure: {err}")
            sys.exit(1)

    def run(self) -> None:
        self._run_update_repo_loop()

        app = dash.Dash(__name__)
        app.layout = self._make_layout  # assign a method to recreate layout on every page refresh
        app.run_server(debug=True)

    def _run_update_repo_loop(self) -> None:
        Thread(target=self._update_repo_loop, daemon=True).start()

    def _update_repo_loop(self) -> None:
        data_lookback_seconds = self._config.data_update_lookback_seconds
        update_period_seconds = self._config.data_update_period_seconds

        while True:
            try:
                self._cached_repo.update(data_lookback_seconds)
                logger.info(f"Update repo successful. Next update in {update_period_seconds} seconds")
            except Exception as err:
                logger.exception(f"Update repo failed: {str(err)}. Next attempt in {update_period_seconds} seconds")

            time.sleep(update_period_seconds)

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
