from datetime import datetime, timedelta, timezone
from typing import List
from pprint import pprint

from generated.synthetics_http_client.synthetics import ApiClient
from generated.synthetics_http_client.synthetics import Configuration
from generated.synthetics_http_client.synthetics import ApiException
from generated.synthetics_http_client.synthetics.api.synthetics_data_service_api import (
    SyntheticsDataServiceApi,
)
from generated.synthetics_http_client.synthetics.api.synthetics_data_service_api import (
    V202101beta1GetHealthForTestsRequest,
)
from generated.synthetics_http_client.synthetics.model.v202101beta1_mesh_response import (
    V202101beta1MeshResponse,
)
from infrastructure.data_access.http.api_client import KentikAPI
from domain.model import MeshResults, MeshRow, MeshColumn, Metric


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
            print("Exception when calling SyntheticsDataServiceApi->get_health_for_tests: %s\n" % e)


def time_utc(time_travel_minutes: int) -> datetime:
    return (datetime.utcnow() + timedelta(minutes=time_travel_minutes)).replace(tzinfo=timezone.utc)


def transform_to_internal_mesh(input: V202101beta1MeshResponse) -> MeshResults:
    mesh = MeshResults()
    for input_row in input:
        columns: List[MeshColumn] = []
        for input_column in input_row.columns:
            jitter = Metric(
                health=input_column.metrics.jitter.health,
                value=int(input_column.metrics.jitter.value),
            )
            latency = Metric(
                health=input_column.metrics.latency.health,
                value=int(input_column.metrics.latency.value),
            )
            packet_loss = Metric(
                health=input_column.metrics.packet_loss.health,
                value=int(input_column.metrics.packet_loss.value),
            )
            column = MeshColumn(
                name=input_column.name,
                alias=input_column.alias,
                target=input_column.target,
                jitter=jitter,
                latency=latency,
                packet_loss=packet_loss,
            )
            columns.append(column)
        row = MeshRow(
            name=input_row.name,
            alias=input_row.alias,
            id=input_row.id,
            ip=input_row.ip,
            local_ip=input_row.local_ip,
            columns=columns,
        )
        mesh.append_row(row)
    return mesh
