from datetime import datetime, timedelta, timezone
from pprint import pprint
from typing import List

from domain.model import MeshColumn, MeshResults, MeshRow, Metric
from generated.synthetics_http_client.synthetics import ApiClient, ApiException, Configuration
from generated.synthetics_http_client.synthetics.api.synthetics_data_service_api import (
    SyntheticsDataServiceApi, V202101beta1GetHealthForTestsRequest)
from generated.synthetics_http_client.synthetics.model.v202101beta1_mesh_column import V202101beta1MeshColumn
from generated.synthetics_http_client.synthetics.model.v202101beta1_mesh_response import V202101beta1MeshResponse
from infrastructure.data_access.http.api_client import KentikAPI


class SyntheticsRepo:
    def __init__(self, email, token: str) -> None:
        self._api_client = KentikAPI(email=email, token=token)

    def get_mesh_test_results(self, test_id: str) -> MeshResults:
        try:
            start = time_utc(time_travel_minutes=-5)
            end = time_utc(time_travel_minutes=0)
            request = V202101beta1GetHealthForTestsRequest(ids=[test_id], start_time=start, end_time=end, augment=True)

            response = self._api_client.synthetics.get_health_for_tests(request)

            # TODO: error handling when no health items received
            return transform_to_internal_mesh(response.health[0].mesh)
        except ApiException as e:
            print(f"Exception when calling SyntheticsDataServiceApi->get_health_for_tests: {e}\n")


def time_utc(time_travel_minutes: int) -> datetime:
    return (datetime.utcnow() + timedelta(minutes=time_travel_minutes)).replace(tzinfo=timezone.utc)


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
