import socket
import json
import joblib
import customtkinter

from threading import Lock, Thread
from apscheduler.schedulers.background import  BackgroundScheduler
from scapy.all import sniff
from flow_manager import FlowManager
from signal_manager import SignalManager
from alert_manager import AlertManager
from display_gui import DisplayGUI

CONFIG_PATH = "src/config.json"
MODEL_PATH = "src/models/all_attacks_random_forest_model_v1.pkl"

def sniff_packets(flow_manager: FlowManager):
    sniff(filter="ip", prn=flow_manager.packet_callback, store=False)

if __name__ == "__main__":
    with open(CONFIG_PATH, 'r') as file:
        config = json.load(file)

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(("8.8.8.8", 80))
        ipv4_address = s.getsockname()[0]

    model = joblib.load(MODEL_PATH)

    flow_mutex = Lock()

    customtkinter.set_appearance_mode("Dark")
    display_gui = DisplayGUI()
    alert_manager = AlertManager()
    flow_manager = FlowManager(ipv4_address, flow_mutex)
    signal_manager = SignalManager(flow_manager, alert_manager, model, flow_mutex, config["attack_probability_threshold"], display_gui)
    scheduler = BackgroundScheduler()
    scheduler.add_job(signal_manager.scan_flows, "interval", seconds=config["scan_frequency"])
    scheduler.start()

    sniff_thread = Thread(target=sniff_packets, args=(flow_manager, ), daemon=True)
    sniff_thread.start()

    display_gui.mainloop()
    scheduler.shutdown()