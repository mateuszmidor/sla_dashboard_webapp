#!/usr/bin/env bash

# Required KentikAPI credentials as environment variables: KTAPI_AUTH_TOKEN, KTAPI_AUTH_EMAIL

OUTPUT_FILENAME="mesh.json"
TEST_ID="3541"
TEST_WINDOW_START="2021-08-03T12:45:00.0+02:00"
TEST_WINDOW_END="2021-08-03T12:50:00.0+02:00"

function get_tests() {
    echo "Fetching test"
    {
        echo '"test-response":'
        curl --location --request GET "https://synthetics.api.kentik.com/synthetics/v202101beta1/tests/$TEST_ID" \
            --header "X-CH-Auth-API-Token: $KTAPI_AUTH_TOKEN" \
            --header "X-CH-Auth-Email: $KTAPI_AUTH_EMAIL" \
            --header 'Content-Type: application/json'
        echo ""
    } >>"$OUTPUT_FILENAME"
}

function get_agents() {
    echo "Fetching agents"
    {
        echo '"agents-response":'
        curl --location --request GET 'https://synthetics.api.kentik.com/synthetics/v202101beta1/agents' \
            --header "X-CH-Auth-API-Token: $KTAPI_AUTH_TOKEN" \
            --header "X-CH-Auth-Email: $KTAPI_AUTH_EMAIL" \
            --header 'Content-Type: application/json'
        echo ""
    } >>"$OUTPUT_FILENAME"
}

function get_health() {
    echo "Fetching health"
    {
        echo '"health-tests-response":'
        curl --location --request POST 'https://synthetics.api.kentik.com/synthetics/v202101beta1/health/tests' \
            --header "X-CH-Auth-API-Token: $KTAPI_AUTH_TOKEN" \
            --header "X-CH-Auth-Email: $KTAPI_AUTH_EMAIL" \
            --header 'Content-Type: application/json' \
            --data-raw "{
            \"ids\":[\"$TEST_ID\"],
            \"startTime\":\"$TEST_WINDOW_START\",
            \"endTime\":\"$TEST_WINDOW_END\",
            \"augment\": true
        }"
        echo ""
    } >>"$OUTPUT_FILENAME"
}

# Build the mesh test results file
echo "{" >"$OUTPUT_FILENAME"
get_tests
echo "," >>"$OUTPUT_FILENAME"
get_agents
echo "," >>"$OUTPUT_FILENAME"
get_health
echo "}" >>"$OUTPUT_FILENAME"