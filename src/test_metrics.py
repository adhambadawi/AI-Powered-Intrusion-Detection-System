import unittest
from metrics import *
from data_models.flow_packet import FlowPacket, Direction

class TestMetrics(unittest.TestCase):
    def test_filter_packets(self):
        packets = [
            FlowPacket("TCP", Direction.FORWARD, "source", "dest", 55555, 55555, 0, 100, 50, set()),
            FlowPacket("TCP", Direction.BACKWARD, "source", "dest", 55555, 55555, 1, 100, 50, set()),
            FlowPacket("TCP", Direction.FORWARD, "source", "dest", 55555, 55555, 2, 100, 50, set()),
        ]

        filtered_packets = filter_packets(packets, Direction.FORWARD)
        self.assertEqual(2, len(filtered_packets))
        for packet in filtered_packets:
            self.assertEqual(Direction.FORWARD, packet.direction)

    def test_interarrival_time(self):
        packets = [
            FlowPacket("TCP", Direction.FORWARD, "source", "dest", 55555, 55555, 0, 100, 50, set()),
            FlowPacket("TCP", Direction.BACKWARD, "source", "dest", 55555, 55555, 1, 100, 50, set()),
            FlowPacket("TCP", Direction.FORWARD, "source", "dest", 55555, 55555, 2, 100, 50, set()),
        ]

        iat = interarrival_time(packets)
        
        self.assertEqual(1, iat["mean"])
        self.assertEqual(0, iat["stdev"])
        self.assertEqual(1, iat["max"])

    def test_flag_count(self):
        packets = [
            FlowPacket("TCP", Direction.FORWARD, "source", "dest", 55555, 55555, 0, 100, 50, {"F1", "F2"}),
            FlowPacket("TCP", Direction.BACKWARD, "source", "dest", 55555, 55555, 1, 100, 50, {"F2", "F3"}),
            FlowPacket("TCP", Direction.FORWARD, "source", "dest", 55555, 55555, 2, 100, 50, {"F1", "F3"}),
        ]

        self.assertEqual(2, flag_count(packets, "F1"))

    def test_segment_size(self):
        packets = [
            FlowPacket("TCP", Direction.FORWARD, "source", "dest", 55555, 55555, 0, 100, 10, {"F1", "F2"}),
            FlowPacket("TCP", Direction.BACKWARD, "source", "dest", 55555, 55555, 1, 100, 20, {"F2", "F3"}),
            FlowPacket("TCP", Direction.FORWARD, "source", "dest", 55555, 55555, 2, 100, 30, {"F1", "F3"}),
        ]

        self.assertEqual(20, segment_size(packets)["mean"])

    def test_header_length(self):
        packets = [
            FlowPacket("TCP", Direction.FORWARD, "source", "dest", 55555, 55555, 0, 100, 10, {"F1", "F2"}),
            FlowPacket("TCP", Direction.BACKWARD, "source", "dest", 55555, 55555, 1, 100, 20, {"F2", "F3"}),
            FlowPacket("TCP", Direction.FORWARD, "source", "dest", 55555, 55555, 2, 100, 30, {"F1", "F3"}),
        ]

        self.assertEqual(240, header_length(packets))

if __name__ == "__main__":
    unittest.main()