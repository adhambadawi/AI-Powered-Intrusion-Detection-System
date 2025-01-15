import socket
import json
import joblib

from apscheduler.schedulers.background import  BackgroundScheduler
from scapy.all import sniff
from flow_manager import FlowManager
from signal_manager import SignalManager
from alert_manager import AlertManager

CONFIG_PATH = "src/config.json"
MODEL_PATH = "src/models/dos_random_forest_v1.pkl"

if __name__ == "__main__":
    with open(CONFIG_PATH, 'r') as file:
        config = json.load(file)

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(("8.8.8.8", 80))
        ipv4_address = s.getsockname()[0]

    model = joblib.load(MODEL_PATH)

    alert_manager = AlertManager()
    flow_manager = FlowManager(ipv4_address)
    signal_manager = SignalManager(flow_manager, alert_manager, model, config["attack_probability_threshold"])

    scheduler = BackgroundScheduler()
    scheduler.add_job(signal_manager.scan_flows, "interval", seconds=config["scan_frequency"])
    scheduler.start()

    print("[INFO] Starting packet capture.")
    try:
        sniff(filter="ip", prn=flow_manager.packet_callback, store=False)
    finally:
        print("[INFO] Packet capture ended.")
        scheduler.shutdown()
