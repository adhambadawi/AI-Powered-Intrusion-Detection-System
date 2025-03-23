import csv

import pandas as pd

from datetime import datetime
from src.flow_manager import FlowManager
from src.display_gui import DisplayGUI
from src.data_models.flow_packet import Direction
from src.data_models.alert import Alert
from src.exceptions.exceptions import TooFewPacketsInFlowException
from src.metrics import segment_size, interarrival_time, packet_length, flag_count, header_length, packet_count

FEATURES = [
    "Avg_Bwd_Segment_Size",
    "Packet_Length_Variance",
    "Total_Length_of_Bwd_Packets",
    "Destination_Port",
    "PSH_Flag_Count",
    "Total_Length_of_Fwd_Packets",
    "Bwd_Header_Length",
    "Fwd_Packet_Length_Max",
    "act_data_pkt_fwd",
    "Fwd_Header_Length.1",
    "Fwd_IAT_Max",
    "Fwd_Packet_Length_Mean",
    "Flow_IAT_Mean",
    "Packet_Length_Std",
    "Flow_IAT_Std",
    "Average_Packet_Size",
    "Fwd_IAT_Std"
]

class SignalManager:
    """The SignalManager class is responsible for preprocessing flow data into model inputs, generating
    signals using the model and passing signals to the AlertManager
    """
    def __init__(self, flow_manager: FlowManager, model, flow_mutex, attack_probability_threshold: float, display_gui: DisplayGUI):
        self._flow_manager = flow_manager
        self._model = model
        self._flow_mutex = flow_mutex
        self._attack_probability_threshold = attack_probability_threshold
        self._display_gui = display_gui

    def _predict_attack_probability(self, input_vector: pd.DataFrame) -> float:
        return self._model.predict_proba(input_vector)[0][1]
    
    def _log_alert(self, alert: Alert, output_path: str):
        if output_path == "":
            return # Don't attempt to log outputs if an output path isn't set
        
        with open(output_path, mode="a") as file:
            writer = csv.writer(file)
            writer.writerow(alert.to_csv())

    def scan_flows(self):
        """Generate signals for a each network flow
        """
        with self._flow_mutex:
            flows = []
            for flow in self._flow_manager.get_flows():
                try:
                    segment_size_metrics_backward = segment_size(flow.packets, Direction.BACKWARD)
                    packet_length_metrics = packet_length(flow.packets)
                    packet_length_metrics_backward = packet_length(flow.packets, Direction.BACKWARD)
                    packet_length_metrics_forward = packet_length(flow.packets, Direction.FORWARD)
                    iat_metrics = interarrival_time(flow.packets)
                    iat_metrics_forward = interarrival_time(flow.packets, Direction.FORWARD)
                    psh_flag_count = flag_count(flow.packets, "PSH")
                    bwd_header_length = header_length(flow.packets, Direction.BACKWARD)
                    fwd_header_length = header_length(flow.packets, Direction.FORWARD)
                    act_data_pkt_fwd = packet_count(flow.packets, Direction.FORWARD)
                except TooFewPacketsInFlowException:
                    # Cannot continue if there are too few packets in the flow to calculate the necessary flow metrics
                    flows.append((flow, 0))
                    continue
                
                input_vector = pd.DataFrame([[
                    segment_size_metrics_backward["mean"],
                    packet_length_metrics["variance"],
                    packet_length_metrics_backward["sum"],
                    flow.destination_port,
                    psh_flag_count,
                    packet_length_metrics_forward["sum"],
                    bwd_header_length,
                    packet_length_metrics_forward["max"],
                    act_data_pkt_fwd,
                    fwd_header_length,
                    iat_metrics_forward["max"],
                    packet_length_metrics_forward["mean"],
                    iat_metrics["mean"],
                    packet_length_metrics["stdev"],
                    iat_metrics["stdev"],
                    packet_length_metrics["mean"],
                    iat_metrics_forward["stdev"]
                ]], columns=FEATURES) # Input vector for model

                attack_probability = self._predict_attack_probability(input_vector)
                if attack_probability >= self._display_gui.get_settings()["attack_probability_threshold"]:
                    self._display_gui.alert_generated(flow, attack_probability)
                    self._log_alert(Alert(datetime.now(), attack_probability, flow), self._display_gui.get_settings()["alert_log_output_path"])

                flows.append((flow, attack_probability))

            self._display_gui.update_flows(flows)
