from dataclasses import dataclass
from src.data_models.flow_packet import FlowPacket
from datetime import datetime

@dataclass
class Flow:
    """Class for representing a flow"""
    packets: list[FlowPacket]
    source_ip: str
    destination_ip: str
    source_port: int
    destination_port: int
    first_packet_timestamp: int
    last_packet_timestamp: int

    def __repr__(self):
        return f"Source IP: {self.source_ip}\nDestination IP: {self.destination_ip}\nSource port: {self.source_port}\nDestination port: {self.destination_port}\nFirst packet timestamp: {datetime.fromtimestamp(self.first_packet_timestamp / 1000000).strftime("%Y-%m-%d %H:%M:%S")}\nLast packet timestamp: {datetime.fromtimestamp(self.last_packet_timestamp / 1000000).strftime("%Y-%m-%d %H:%M:%S")}"

    def to_csv(self):
        return [self.source_ip, self.destination_ip, self.source_port, self.destination_port, self.first_packet_timestamp, self.last_packet_timestamp]