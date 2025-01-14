import socket
from scapy.all import sniff
from flow_manager import FlowManager
from signal_manager import SignalManager
from alert_manager import AlertManager

if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(("8.8.8.8", 80))
        ipv4_address = s.getsockname()[0]

    alert_manager = AlertManager()
    signal_manager = SignalManager(alert_manager, 0.95)
    flow_manager = FlowManager(signal_manager, ipv4_address)
    print("Starting packet capture...")
    try:
        sniff(filter="ip", prn=flow_manager.packet_callback, store=False, timeout=60)  # Capture for 60 seconds
    finally:
        print("Packet capture finished.")