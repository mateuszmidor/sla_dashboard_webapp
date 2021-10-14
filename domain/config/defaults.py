"""Default values for config params in Config class"""

from domain.metric import MetricType

data_request_interval_periods = 1
data_history_length_periods = 60
data_min_periods = 2
timeout_seconds = (30.0, 30.0)
logging_level = "INFO"
agent_label = "{name}"
show_measurement_values = True
metric_type = MetricType.PACKET_LOSS.value
