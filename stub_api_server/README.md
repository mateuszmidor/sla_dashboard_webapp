# stub_api_server

This webserver allows for testing the sla_dashboard_webapp in offline mode, serving mesh test responses from a file.

## Run

```bash
RESPONSE_FILE_PATH="stub_api_server/mesh_5x5_40%.json" FLASK_ENV=development FLASK_APP=stub_api_server flask run --port=9050
```
or
```bash
RESPONSE_FILE_PATH="stub_api_server/mesh_5x5_80%.json" FLASK_ENV=development FLASK_APP=stub_api_server flask run --port=9050
```
or
```bash
RESPONSE_FILE_PATH="stub_api_server/mesh_5x5_100%.json" FLASK_ENV=development FLASK_APP=stub_api_server flask run --port=9050
```
or
```bash
RESPONSE_FILE_PATH="stub_api_server/mesh_5x5_8%.json" FLASK_ENV=development FLASK_APP=stub_api_server flask run --port=9050
```
or
```bash
RESPONSE_FILE_PATH="stub_api_server/mesh_5x5.json" FLASK_ENV=development FLASK_APP=stub_api_server flask run --port=9050
```
or
```bash
RESPONSE_FILE_PATH="stub_api_server/mesh_20x20.json" FLASK_ENV=development FLASK_APP=stub_api_server flask run --port=9050
```
