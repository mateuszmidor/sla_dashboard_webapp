import urllib.parse as urlparse
from typing import Tuple

from domain.metric_type import MetricType
from domain.types import AgentID


def encode_matrix_path(metric: MetricType) -> str:
    if metric == MetricType.PACKET_LOSS:
        return "/packet_loss"
    if metric == MetricType.JITTER:
        return "/jitter"
    if metric == MetricType.LATENCY:
        return "/latency"
    return "/"


def encode_chart_path(from_agent, to_agent: AgentID) -> str:
    return f"/chart?from={from_agent}&to={to_agent}"


def decode_chart_path(path: str) -> Tuple[AgentID, AgentID]:
    params = urlparse.parse_qs(urlparse.urlparse(path).query)
    return params["from"][0], params["to"][0]


def is_latency(pathname: str) -> bool:
    return pathname == "/" or pathname == "/latency"


def is_jitter(pathname: str) -> bool:
    return pathname == "/jitter"


def is_packetloss(pathname: str):
    return pathname == f"/packet_loss"


def is_charts(pathname: str):
    return pathname == "/chart" or pathname.startswith("/chart?")
