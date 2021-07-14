# stub_api_server

This webserver allows for testing the sla_dashboard_webapp in offline mode, serving mesh test responses from a file.

## Run

```bash
RESPONSE_FILE_PATH="stub_api_server/mesh_5x5.json" FLASK_ENV=development FLASK_APP=stub_api_server flask run --port=9050
```
