from dataclasses import dataclass
from enum import Enum

class Direction(Enum):
    FORWARD = 1
    BACKWARD = 2
    BIDIRECTIONAL = 3

@dataclass
class FlowPacket:
    """Class for representing packets in a flow"""
    protocol: str
    direction: Direction
    source_ip: str
    destination_ip: str
    source_port: int
    destination_port: int
    arrival_time: int
    size: int
    segment_size: int
    flags: set