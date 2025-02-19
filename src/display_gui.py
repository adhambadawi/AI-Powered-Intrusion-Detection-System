import tkinter
import customtkinter
from tkinter import messagebox
from data_models.flow import Flow

class FlowWindow(customtkinter.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)

        self.label_list = []
        self.button_list = []
        self._flows = set({})

    def add_flow(self, flow: Flow, attack_probability: str):
        key = f"{flow.source_ip}:{flow.source_port}->{flow.destination_ip}:{flow.destination_port}"
        if key in self._flows:
            return

        self._flows.add(key)
        label = customtkinter.CTkLabel(self, text=f"{flow.source_ip}:{flow.source_port}->{flow.destination_ip}:{flow.destination_port}", compound="left", padx=5, anchor="w")
        button = customtkinter.CTkButton(self, text="View", width=100, height=24)
        button.configure(command=lambda: messagebox.showinfo("Flow Info", f"{flow}\nAttack probability: {attack_probability}"))
        label.grid(row=len(self.label_list), column=0, pady=(0, 10), sticky="w")
        button.grid(row=len(self.button_list), column=1, pady=(0, 10), padx=5)
        self.label_list.append(label)
        self.button_list.append(button)

    def clear(self):
        pass

class DisplayGUI(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("ML-Powered IDS")
        self.geometry("600x400")
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._alerts = 0
        self._active_flows_label = customtkinter.CTkLabel(self, text=f"Active flows: 0", font=("Helvetica", 16))
        self._alerts_counter_label = customtkinter.CTkLabel(self, text=f"Alerts: {self._alerts}", font=("Helvetica", 16))
        self._active_flows_label.grid(row=0, column=0, pady=(20, 5))
        self._alerts_counter_label.grid(row=0, column=0, pady=(80, 5))

        self._flow_window = FlowWindow(master=self, width=500, corner_radius=0)
        self._flow_window.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    def alert_generated(self, flow: Flow, attack_probability: float):
        self._alerts += 1
        self._alerts_counter_label.configure(text=f"Alerts: {self._alerts}")
        messagebox.showwarning("Alert", f"DoS attack detected\nAttack probability: {attack_probability}\nFlow:\n{flow}")

    def update_flows(self, flows: list[tuple]):
        self._active_flows_label.configure(text=f"Active flows: {len(flows)}")
        self._flow_window.clear()
        for flow, attack_probability in flows:
            self._flow_window.add_flow(flow, attack_probability)