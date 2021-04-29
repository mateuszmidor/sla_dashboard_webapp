from dataclasses import dataclass
from domain.model.metric import Metric


@dataclass
class MeshColumn:
    name: str
    alias: str
    target: str  # ip address
    jitter: Metric
    latency: Metric  # eg. value of 200500 means 200.5 milliseconds
    packet_loss: Metric