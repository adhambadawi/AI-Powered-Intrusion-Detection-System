from dataclasses import dataclass
from src.data_models.flow_packet import FlowPacket

@dataclass
class FlowStub:
    """Class for representing a dummy flow for the test stub"""
    row_index: int
    malicious: bool
    packets: list[FlowPacket]
    source_ip: str = "Dummy source"
    destination_ip: str = "Dummy destination"
    source_port: int = 0
    destination_port: int = 0
    first_packet_timestamp: int = 0
    last_packet_timestamp: int = 0

    def __repr__(self):
        return f"Source IP: {self.source_ip}\nDestination IP: {self.destination_ip}\nSource port: {self.source_port}\nDestination port: {self.destination_port}\nFirst packet timestamp: {self.first_packet_timestamp}\nLast packet timestamp: {self.last_packet_timestamp}\nMalicious: {self.malicious}"