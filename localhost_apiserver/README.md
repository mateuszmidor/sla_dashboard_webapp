# localhost_apiserver

This webserver allows for testing the sla_dashboard_webapp in offline mode, serving mesh test responses from a file.

## Run

```bash
RESPONSE_FILE_PATH="localhost_apiserver/mesh_5x5.json" FLASK_ENV=developmentt FLASK_APP=localhost_apiserver flask run --port=9050
```
