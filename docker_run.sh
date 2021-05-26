#!/usr/bin/env bash

docker run \
    --name sla_dashboard \
    --rm \
    -e KTAPI_AUTH_EMAIL="$KTAPI_AUTH_EMAIL" \
    -e KTAPI_AUTH_TOKEN="$KTAPI_AUTH_TOKEN" \
    -v "$(pwd)/data:/app/data" \
    -p 127.0.0.1:8050:8050 \
    sla_dashboard:latest