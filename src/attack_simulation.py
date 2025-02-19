import json
import joblib
import customtkinter

import pandas as pd

from threading import Lock
from apscheduler.schedulers.background import  BackgroundScheduler
from signal_manager_stub import SignalManagerStub
from alert_manager import AlertManager
from display_gui import DisplayGUI

CONFIG_PATH = "src/config.json"
MODEL_PATH = "src/models/dos_random_forest_v1.pkl"
TEST_DATA_PATH = "src/test_data/preprocessed_cicids2017_test_1.csv"

if __name__ == "__main__":
    with open(CONFIG_PATH, 'r') as file:
        config = json.load(file)

    flow_df = pd.read_csv(TEST_DATA_PATH)
    model = joblib.load(MODEL_PATH)

    flow_mutex = Lock()

    alert_manager = AlertManager()
    customtkinter.set_appearance_mode("Dark")
    display_gui = DisplayGUI()
    signal_manager_stub = SignalManagerStub(None, alert_manager, model, flow_mutex, config["attack_probability_threshold"], flow_df, 15, display_gui)

    scheduler = BackgroundScheduler()
    scheduler.add_job(signal_manager_stub.scan_flows, "interval", seconds=config["scan_frequency"])
    scheduler.start()

    display_gui.mainloop()
    scheduler.shutdown()
