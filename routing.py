import logging
import urllib.parse as urlparse
from typing import Tuple

from domain.metric import MetricType
from domain.types import AgentID

MAIN = "/"
MATRIX = "/matrix"
CHART = "/chart"

logger = logging.getLogger("routing")


def encode_matrix_path(metric: MetricType) -> str:
    return f"{MATRIX}?metric={metric.value}"


def decode_matrix_path(path: str) -> MetricType:
    params = urlparse.parse_qs(urlparse.urlparse(path).query)
    try:
        return MetricType(params["metric"][0])
    except (IndexError, KeyError, ValueError):
        logger.error(f"Invalid matrix path: {path}")
        return MetricType.LATENCY


def encode_chart_path(from_agent, to_agent: AgentID) -> str:
    return f"{CHART}?from={from_agent}&to={to_agent}"


def decode_chart_path(path: str) -> Tuple[AgentID, AgentID]:
    params = urlparse.parse_qs(urlparse.urlparse(path).query)
    try:
        return params["from"][0], params["to"][0]
    except (IndexError, KeyError):
        logger.error(f"Invalid chart path: {path}")
        return AgentID(), AgentID()
