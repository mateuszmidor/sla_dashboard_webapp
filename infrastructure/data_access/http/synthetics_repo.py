from datetime import datetime, timedelta, timezone
from typing import List

from domain.model import MeshColumn, MeshResults, MeshRow, Metric

# the below "diable=E0611" is needed as we don't include the generated code into git repo and thus CI linter complains
# pylint: disable=E0611
from generated.synthetics_http_client.synthetics import ApiClient, ApiException, Configuration
from generated.synthetics_http_client.synthetics.api.synthetics_data_service_api import (
    SyntheticsDataServiceApi,
    V202101beta1GetHealthForTestsRequest,
)
from generated.synthetics_http_client.synthetics.model.v202101beta1_mesh_column import V202101beta1MeshColumn
from generated.synthetics_http_client.synthetics.model.v202101beta1_mesh_response import V202101beta1MeshResponse

# pylint: enable=E0611
from infrastructure.data_access.http.api_client import KentikAPI


class SyntheticsRepo:
    """ SyntheticsRepo implements domain.Repo protocol """

    def __init__(self, email, token: str) -> None:
        self._api_client = KentikAPI(email=email, token=token)

    def get_mesh_test_results(self, test_id: str, results_lookback_seconds: int) -> MeshResults:
        try:
            start = time_utc(time_travel_seconds=-results_lookback_seconds)
            end = time_utc(time_travel_seconds=0)

            request = V202101beta1GetHealthForTestsRequest(ids=[test_id], start_time=start, end_time=end, augment=True)
            response = self._api_client.synthetics.get_health_for_tests(request)

            num_results = len(response.health)
            if num_results == 0:
                raise Exception("get_health_for_tests returned 0 items")

            most_recent_result = response.health[num_results - 1].mesh
            return transform_to_internal_mesh(most_recent_result)
        except ApiException as e:
            raise e


def time_utc(time_travel_seconds: int) -> datetime:
    return (datetime.utcnow() + timedelta(seconds=time_travel_seconds)).replace(tzinfo=timezone.utc)


def transform_to_internal_mesh(input: V202101beta1MeshResponse) -> MeshResults:
    mesh = MeshResults()
    for input_row in input:
        row = MeshRow(
            name=input_row.name,
            alias=input_row.alias,
            id=input_row.id,
            ip=input_row.ip,
            local_ip=input_row.local_ip,
            columns=transform_to_internal_mesh_columns(input_row.columns),
        )
        mesh.append_row(row)
    return mesh


def transform_to_internal_mesh_columns(input_columns: List[V202101beta1MeshColumn]) -> List[MeshColumn]:
    columns = []
    for input_column in input_columns:
        column = MeshColumn(
            name=input_column.name,
            alias=input_column.alias,
            id=input_column.id,
            target=input_column.target,
            jitter=Metric(
                health=input_column.metrics.jitter.health,
                value=int(input_column.metrics.jitter.value),
            ),
            latency_microsec=Metric(
                health=input_column.metrics.latency.health,
                value=int(input_column.metrics.latency.value),
            ),
            packet_loss=Metric(
                health=input_column.metrics.packet_loss.health,
                value=int(input_column.metrics.packet_loss.value),
            ),
        )
        columns.append(column)
    return columns
