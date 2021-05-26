from enum import Enum


class Metric(Enum):
    """ Available mesh test metric types """

    LATENCY = "Latency[ms]"
    JITTER = "Jitter[ms]"
    PACKET_LOSS = "Packet loss[%]"
