from data_models.flow_packet import FlowPacket, Direction
from exceptions.exceptions import TooFewPacketsInFlowException
from statistics import mean, stdev, variance

def filter_packets(flow: list[FlowPacket], direction: Direction=Direction.BIDIRECTIONAL) -> list[FlowPacket]:
    """Filter a list of packets to include only the specified direction type

    Args:
        flow (list[FlowPacket]): List of packets in flow
        direction (Direction, optional): Packet direction. Defaults to Direction.BIDIRECTIONAL.

    Returns:
        list[FlowPacket]: List of filtered packets
    """
    return [packet for packet in flow if direction == Direction.BIDIRECTIONAL or direction == packet.direction]

def packet_length(flow: list[FlowPacket], direction: Direction=Direction.BIDIRECTIONAL) -> dict:
    """Calculate metrics for packet lengths in a flow

    Args:
        flow (list[FlowPacket]): List of packets in flow
        direction (Direction, optional): Direction to filter by. Defaults to Direction.BIDIRECTIONAL.

    Returns:
        dict: Contains packet length sum, max, mean, and variance
    """
    packet_lengths = [packet.size for packet in filter_packets(flow, direction)]
    if len(packet_lengths) < 2:
        raise TooFewPacketsInFlowException()
        
    return {
        "sum": sum(packet_lengths),
        "max": max(packet_lengths),
        "mean": mean(packet_lengths),
        "variance": variance(packet_lengths)
    }

def interarrival_time(flow: list[FlowPacket], direction: Direction=Direction.BIDIRECTIONAL) -> dict:
    """Calculate metrics for inter-arrival times (IAT) of packets in flow

    Args:
        flow (list[FlowPacket]): List of packets in flow
        direction (Direction, optional): Filter by packet direction. Defaults to Direction.BIDIRECTIONAL.

    Returns:
        dict: Contains IAT mean and standard deviation
    """
    filtered_packets = filter_packets(flow, direction)
    if len(filtered_packets) < 3:
        raise TooFewPacketsInFlowException()
    
    interarrival_times = [filtered_packets[i].arrival_time - filtered_packets[i - 1].arrival_time for i in range(1, len(filtered_packets))]
    return {"mean": mean(interarrival_times), "stdev": stdev(interarrival_times)}

def segment_size(flow: list[FlowPacket], direction: Direction=Direction.BIDIRECTIONAL) -> dict:
    """Calculate metrics for segment size of packets in a flow

    Args:
        flow (list[FlowPacket]): List of packets in flow
        direction (Direction, optional): Direction to filter by. Defaults to Direction.BIDIRECTIONAL.

    Returns:
        dict: Contains segment size mean
    """
    filtered_packets = filter_packets(flow, direction)
    if len(filtered_packets) < 1:
        raise TooFewPacketsInFlowException()
    
    segment_sizes = [packet.segment_size for packet in filtered_packets]
    return {"mean": mean(segment_sizes)}