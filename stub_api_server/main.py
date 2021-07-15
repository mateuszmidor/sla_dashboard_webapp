import os
import sys
from logging import Logger

from flask import Flask, Response, request


def create_app() -> Flask:
    # create and configure the app
    app = Flask(__name__, instance_relative_config=False)

    # read predefined mesh test response from a file
    http_response_body = load_health_tests_response(app.logger)

    # configure routes
    @app.route("/synthetics/v202101beta1/health/tests", methods=["GET", "POST"])
    def health_tests():
        return Response(response=http_response_body, mimetype="application/json")

    @app.route("/shutdown", methods=["GET"])
    def shutdown():
        shutdown = request.environ.get("werkzeug.server.shutdown")
        if not shutdown:
            raise RuntimeError("Not running with the Werkzeug Server")
        shutdown()
        return Response(response="Server shutdown now", mimetype="text/html")

    return app


def load_health_tests_response(logger: Logger) -> str:
    response_file_path = os.getenv("RESPONSE_FILE_PATH")
    if not response_file_path:
        logger.critical('Environment variable "RESPONSE_FILE_PATH" is required')
        sys.exit(1)
    logger.info(f'Serving mesh test results from "{response_file_path}"')
    with open(response_file_path, mode="r") as f:
        return f.read()
