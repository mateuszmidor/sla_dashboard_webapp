import os
import sys
from typing import Tuple

import dash

from infrastructure.data_access.http.synthetics_repo import SyntheticsRepo
from presentation.matrix_view import make_mesh_test_matrix_layout


def run_web_server() -> None:
    email, token = get_auth_email_token()
    repo = SyntheticsRepo(email, token)
    mesh_test_results = repo.get_mesh_test_results("3541")

    app = dash.Dash(__name__)
    app.layout = make_mesh_test_matrix_layout(mesh_test_results)
    app.run_server(debug=True)


def get_auth_email_token() -> Tuple[str, str]:
    try:
        email = os.environ["KTAPI_AUTH_EMAIL"]
        token = os.environ["KTAPI_AUTH_TOKEN"]
        return email, token
    except KeyError:
        print("You have to specify KTAPI_AUTH_EMAIL and KTAPI_AUTH_TOKEN first")
        sys.exit(1)


if __name__ == "__main__":
    run_web_server()