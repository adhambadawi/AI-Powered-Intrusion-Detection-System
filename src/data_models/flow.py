from dataclasses import dataclass
from data_models.flow_packet import FlowPacket

@dataclass
class Flow:
    """Class for representing packets in a flow"""
    packets: list[FlowPacket]
    source_ip: str
    destination_ip: str
    source_port: int
    destination_port: int
    first_packet_timestamp: int
    last_packet_timestamp: int