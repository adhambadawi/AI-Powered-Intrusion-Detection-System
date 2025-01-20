import pandas as pd

from alert_manager import AlertManager
from flow_manager import FlowManager
from data_models.flow_stub import FlowStub
from signal_manager import SignalManager
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

class SignalManagerStub(SignalManager):
    """The SignalManagerStub class is a test-stub to test the data feed with pre-set flow data
    """
    def __init__(self, flow_manager: FlowManager, alert_manager: AlertManager, model, flow_mutex, attack_probability_threshold: float, flow_df: pd.DataFrame, predictions_per_scan: int):
        self._flow_df = flow_df
        self._predictions_per_scan = predictions_per_scan
        self._flow_index = 0
        super().__init__(flow_manager, alert_manager, model, flow_mutex, attack_probability_threshold)

    def scan_flows(self):
        """Generate signals for a each network flow
        """
        for _ in range(self._predictions_per_scan):
            input_vector = pd.DataFrame([[
                self._flow_df.iloc[self._flow_index][feature] for feature in FEATURES
            ]], columns=FEATURES)

            if self._predict_attack_probability(input_vector) >= self._attack_probability_threshold:
                flow = FlowStub(self._flow_index, self._flow_df.iloc[self._flow_index]["Attack"] == 1)
                self._alert_manager.generate_alert(flow)

            self._flow_index = (self._flow_index + 1) % len(self._flow_df)