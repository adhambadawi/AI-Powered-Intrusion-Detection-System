import customtkinter
from PIL import Image
from tkinter import messagebox
from src.data_models.flow import Flow

class SettingsWindow(customtkinter.CTkToplevel):
    def __init__(self, parent, settings: dict):
        super().__init__(parent)
        self.parent = parent
        self.title("Settings")
        self.geometry("300x200")

        # Threshold value (decimal between 0 and 1)
        self.attack_probability_threshold_label = customtkinter.CTkLabel(self, text="Attack Probability Threshold:")
        self.attack_probability_threshold_label.pack(pady=(10, 0))
        self.attack_probability_threshold_entry = customtkinter.CTkEntry(self)
        self.attack_probability_threshold_entry.pack(pady=5)
        self.attack_probability_threshold_entry.insert(0, settings["attack_probability_threshold"])  # Default value

        # Integer option (integer >= 1)
        self.alert_log_output_path_label = customtkinter.CTkLabel(self, text="Alert Log Output Path:")
        self.alert_log_output_path_label.pack(pady=(10, 0))
        self.alert_log_output_path_entry = customtkinter.CTkEntry(self)
        self.alert_log_output_path_entry.pack(pady=5)
        self.alert_log_output_path_entry.insert(0, settings["alert_log_output_path"])  # Default value

        # Save Button
        self.save_button = customtkinter.CTkButton(self, text="Save", command=self.save_settings)
        self.save_button.pack(pady=10)

    def save_settings(self):
        try:
            attack_probability_threshold = float(self.attack_probability_threshold_entry.get())
            alert_log_output_path = self.alert_log_output_path_entry.get()

            if not (0 <= attack_probability_threshold <= 1):
                raise ValueError("Threshold must be between 0 and 1.")

            self.parent.handle_update_settings({"attack_probability_threshold": attack_probability_threshold, "alert_log_output_path": alert_log_output_path})
            self.destroy()  # Close window after saving

        except ValueError as e:
            print(f"Error: {e}")

class FlowWindow(customtkinter.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)  # 5 data columns + 1 button column

        self.row_index = 1  # Start from row 1, row 0 will be header
        self._flows = {}

        # Add headers
        headers = ["Source IP", "Destination IP", "Source Port", "Destination Port", "Attack Probability", "Details"]
        for col_index, header in enumerate(headers):
            header_label = customtkinter.CTkLabel(self, text=header, font=("Helvetica", 12, "bold"))
            header_label.grid(row=0, column=col_index, padx=5, pady=(0, 10), sticky="w")

    def add_flow(self, flow: Flow, attack_probability: str):
        key = f"{flow.source_ip}:{flow.source_port}->{flow.destination_ip}:{flow.destination_port}"
        if key in self._flows:
            # Update button command if flow already exists
            self._flows[key]["button"].configure(command=lambda: messagebox.showinfo("Flow Info", f"{flow}\nAttack probability: {attack_probability}"))
            self._flows[key]["attack_label"].configure(text=str(attack_probability))
        else:
            # Create and place labels
            source_ip_label = customtkinter.CTkLabel(self, text=flow.source_ip)
            destination_ip_label = customtkinter.CTkLabel(self, text=flow.destination_ip)
            source_port_label = customtkinter.CTkLabel(self, text=str(flow.source_port))
            destination_port_label = customtkinter.CTkLabel(self, text=str(flow.destination_port))
            attack_label = customtkinter.CTkLabel(self, text=str(attack_probability))

            source_ip_label.grid(row=self.row_index, column=0, padx=5, pady=2, sticky="w")
            destination_ip_label.grid(row=self.row_index, column=1, padx=5, pady=2, sticky="w")
            source_port_label.grid(row=self.row_index, column=2, padx=5, pady=2, sticky="w")
            destination_port_label.grid(row=self.row_index, column=3, padx=5, pady=2, sticky="w")
            attack_label.grid(row=self.row_index, column=4, padx=5, pady=2, sticky="w")

            # Add View button
            button = customtkinter.CTkButton(self, text="View", width=60)
            button.configure(command=lambda: messagebox.showinfo("Flow Info", f"{flow}\nAttack probability: {attack_probability}"))
            button.grid(row=self.row_index, column=5, padx=5, pady=2, sticky="w")

            # Save references
            self._flows[key] = {
                "button": button,
                "attack_label": attack_label,
                "flow": flow
            }

            self.row_index += 1

    def clear(self):
        # Clear all flow rows (keep header row)
        for widget in self.winfo_children():
            row = widget.grid_info().get("row", None)
            if row is not None and row != 0:
                widget.destroy()
        self._flows.clear()
        self.row_index = 1

class DisplayGUI(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("ML-Powered IDS")
        self.geometry("600x400")
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        logo_image = customtkinter.CTkImage(
            dark_image=Image.open("src/resources/logo.png"),
            size=(150, 150)
        )

        self.logo_label = customtkinter.CTkLabel(self, image=logo_image, text="")
        self.logo_label.grid(row=0, column=0, pady=(20, 5))

        self._alerts = 0
        self._active_flows_label = customtkinter.CTkLabel(self, text=f"Active flows: 0", font=("Helvetica", 16))
        self._alerts_counter_label = customtkinter.CTkLabel(self, text=f"Alerts: {self._alerts}", font=("Helvetica", 16))
        self._active_flows_label.grid(row=1, column=0, pady=(20, 5))
        self._alerts_counter_label.grid(row=1, column=0, pady=(80, 5))

        self.settings_button = customtkinter.CTkButton(self, text="Settings", command=self.open_settings)
        self.settings_button.grid(row=2, column=0, padx=10, pady=10)

        self.sort_by_label = customtkinter.CTkLabel(self, text="Sort by:")
        self.sort_by_label.grid(row=3, column=0, pady=(5, 0), sticky="w")

        # Sorting dropdown
        self.sorting_option = customtkinter.StringVar(value="First Packet Timestamp")
        self.sorting_dropdown = customtkinter.CTkComboBox(
            self,
            values=["First Packet Timestamp", "Last Packet Timestamp", "Attack Probability"],
            variable=self.sorting_option,
            command=self.update_flows
        )
        self.sorting_dropdown.grid(row=4, column=0, pady=(5, 0), sticky="w")

        self._flow_window = FlowWindow(master=self, width=500, corner_radius=0)
        self._flow_window.grid(row=5, column=0, padx=10, pady=10, sticky="nsew")

        self._settings = {"attack_probability_threshold": 0.95, "alert_log_output_path": ""}
        self._flows_data = []  # Store raw flows to allow re-sorting

    def alert_generated(self, flow: Flow, attack_probability: float):
        self._alerts += 1
        self._alerts_counter_label.configure(text=f"Alerts: {self._alerts}")
        messagebox.showwarning("Alert", f"DoS attack detected\nAttack probability: {attack_probability}\nFlow:\n{flow}")

    def update_flows(self, flows: list[tuple] = None):
        """Sorts and updates the flow display."""
        if flows:
            self._flows_data = flows  # Store flows for re-sorting

        self._active_flows_label.configure(text=f"Active flows: {len(self._flows_data)}")

        # Sort flows based on selected option
        sort_by = self.sorting_option.get()
        if sort_by == "First Packet Timestamp":
            self._flows_data.sort(key=lambda f: f[0].first_packet_timestamp)
        elif sort_by == "Last Packet Timestamp":
            self._flows_data.sort(key=lambda f: f[0].last_packet_timestamp)
        elif sort_by == "Attack Probability":
            self._flows_data.sort(key=lambda f: f[1], reverse=True)  # Highest probability first

        self._flow_window.clear()
        for flow, attack_probability in self._flows_data:
            self._flow_window.add_flow(flow, attack_probability)

    def handle_update_settings(self, settings: dict):
        self._settings = settings

    def get_settings(self) -> dict:
        return self._settings

    def open_settings(self):
        settings_window = SettingsWindow(self, self._settings)
        settings_window.grab_set()
