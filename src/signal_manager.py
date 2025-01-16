import pandas as pd

from alert_manager import AlertManager
from flow_manager import FlowManager
from data_models.flow import Flow
from data_models.flow_packet import Direction
from exceptions.exceptions import TooFewPacketsInFlowException
from metrics import segment_size, interarrival_time, packet_length

FEATURES = [
    "Avg_Bwd_Segment_Size",
    "Max_Packet_Length",
    "Average_Packet_Size",
    "Flow_IAT_Mean",
    "Total_Length_of_Bwd_Packets",
    "Destination_Port",
    "Fwd_IAT_Mean",
    "Fwd_IAT_Std",
    "Packet_Length_Variance"
]

class SignalManager:
    """The SignalManager class is responsible for preprocessing flow data into model inputs, generating
    signals using the model and passing signals to the AlertManager
    """
    def __init__(self, flow_manager: FlowManager, alert_manager: AlertManager, model, flow_mutex, attack_probability_threshold: float):
        self._flow_manager = flow_manager
        self._alert_manager = alert_manager
        self._model = model
        self._flow_mutex = flow_mutex
        self._attack_probability_threshold = attack_probability_threshold

    def _predict_attack_probability(self, input_vector: pd.DataFrame) -> float:
        return self._model.predict_proba(input_vector)[0][1]

    def scan_flows(self):
        """Generate signals for a each network flow
        """
        with self._flow_mutex:
            for flow in self._flow_manager.get_flows():
                try:
                    segment_size_metrics_backward = segment_size(flow.packets, Direction.BACKWARD)
                    packet_length_metrics = packet_length(flow.packets)
                    packet_length_metrics_backward = packet_length(flow.packets, Direction.BACKWARD)
                    iat_metrics = interarrival_time(flow.packets)
                    iat_metrics_forward = interarrival_time(flow.packets, Direction.FORWARD)
                except TooFewPacketsInFlowException:
                    # Cannot continue if there are too few packets in the flow to calculate the necessary flow metrics
                    return
                
                input_vector = pd.DataFrame([[
                    segment_size_metrics_backward["mean"],
                    packet_length_metrics["max"],
                    packet_length_metrics["mean"],
                    iat_metrics["mean"],
                    packet_length_metrics_backward["sum"],
                    flow.destination_port,
                    iat_metrics_forward["mean"],
                    iat_metrics_forward["stdev"],
                    packet_length_metrics["variance"]
                ]], columns=FEATURES) # Input vector for model

                if self._predict_attack_probability(input_vector) >= self._attack_probability_threshold:
                    self._alert_manager.generate_alert(flow)
