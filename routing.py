import logging
import urllib.parse as urlparse
from enum import Enum
from typing import Tuple

from domain.metric import MetricType
from domain.types import AgentID

logger = logging.getLogger("routing")


class Route(Enum):
    INDEX = "/"
    MATRIX = "/matrix"
    TIME_SERIES = "/time-series"
    UNKNOWN = "[unknown_route]"


def extract_route(pathname: str) -> Route:
    """
    Example:
        pathname: /matrix?metric=Latency
        return:   Route.MATRIX
    """

    route_end_index = pathname.find("?")
    route_str = pathname[:route_end_index] if route_end_index != -1 else pathname
    try:
        return Route(route_str)
    except Exception:
        logger.exception("Unknown route: %s", route_str)
        return Route.UNKNOWN


def encode_matrix_path(metric: MetricType) -> str:
    return f"{Route.MATRIX.value}?metric={metric.value}"


def decode_matrix_path(path: str) -> MetricType:
    params = urlparse.parse_qs(urlparse.urlparse(path).query)
    try:
        return MetricType(params["metric"][0])
    except (IndexError, KeyError, ValueError):
        logger.error(f"Invalid matrix path: {path}")
        return MetricType.LATENCY


def encode_time_series_path(from_agent, to_agent: AgentID) -> str:
    return f"{Route.TIME_SERIES.value}?from={from_agent}&to={to_agent}"


def decode_time_series_path(path: str) -> Tuple[AgentID, AgentID]:
    params = urlparse.parse_qs(urlparse.urlparse(path).query)
    try:
        return params["from"][0], params["to"][0]
    except (IndexError, KeyError):
        logger.error(f"Invalid time series path: {path}")
        return AgentID(), AgentID()
