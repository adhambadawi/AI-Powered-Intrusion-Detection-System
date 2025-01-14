from alert_manager import AlertManager
from data_models.flow import Flow
from data_models.flow_packet import Direction
from exceptions.exceptions import TooFewPacketsInFlowException
from metrics import segment_size, interarrival_time, packet_length

class SignalManager:
    def __init__(self, alert_manager: AlertManager, attack_probability_threshold: float):
        self._alert_manager = alert_manager
        self._attack_probability_threshold = attack_probability_threshold

    def process_input(self, flow: Flow):
        """Generate a signal for a flow

        Args:
            flow (Flow): Flow
        """        
        try:
            segment_size_metrics_backward = segment_size(flow.packets, Direction.BACKWARD)
            packet_length_metrics = packet_length(flow.packets)
            packet_length_metrics_backward = packet_length(flow.packets, Direction.BACKWARD)
            iat_metrics = interarrival_time(flow.packets)
            iat_metrics_forward = interarrival_time(flow.packets, Direction.FORWARD)
        except TooFewPacketsInFlowException:
            # Cannot continue if there are too few packets in the flow to calculate the necessary flow metrics
            return
        
        input_vector = [
            segment_size_metrics_backward["mean"],
            flow.destination_port,
            packet_length_metrics["max"],
            packet_length_metrics["mean"],
            packet_length_metrics_backward["sum"],
            iat_metrics["mean"],
            iat_metrics_forward["mean"],
            iat_metrics_forward["stdev"],
            packet_length_metrics["variance"]
        ] # Input vector for model

        attack_probability = 0 # Placeholder: Replace with function call to model
        if attack_probability >= self._attack_probability_threshold:
            self._alert_manager.generate_alert(flow)
