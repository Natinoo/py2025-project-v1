import tkinter as tk
from tkinter import ttk
import threading
import queue
from datetime import datetime, timedelta
import json
from server.server import NetworkServer


class ServerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sensor Server Monitor")

        # Server configuration
        self.server = None
        self.server_thread = None
        self.running = False
        self.message_queue = queue.Queue()
        self.sensors = {}
        self.history = []  # Przechowuje historię odczytów dla średnich

        # Setup GUI
        self.setup_gui()

        # Start checking for messages
        self.check_messages()
        self.update_sensor_data()

    def setup_gui(self):
        """Setup all GUI components"""
        # Top panel - controls
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.grid(row=0, column=0, sticky="ew")

        ttk.Label(control_frame, text="Port:").grid(row=0, column=0, padx=5)
        self.port_entry = ttk.Entry(control_frame, width=10)
        self.port_entry.grid(row=0, column=1, padx=5)
        self.port_entry.insert(0, "5001")

        self.start_button = ttk.Button(control_frame, text="Start", command=self.start_server)
        self.start_button.grid(row=0, column=2, padx=5)

        self.stop_button = ttk.Button(control_frame, text="Stop", command=self.stop_server, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=3, padx=5)

        # Middle panel - sensor table
        table_frame = ttk.Frame(self.root, padding="10")
        table_frame.grid(row=1, column=0, sticky="nsew")

        # Create treeview
        columns = ('sensor_id', 'value', 'unit', 'timestamp', 'avg_1h', 'avg_12h')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings')

        # Define headings
        self.tree.heading('sensor_id', text='Sensor ID')
        self.tree.heading('value', text='Value')
        self.tree.heading('unit', text='Unit')
        self.tree.heading('timestamp', text='Timestamp')
        self.tree.heading('avg_1h', text='Avg 1h')
        self.tree.heading('avg_12h', text='Avg 12h')

        # Configure columns
        self.tree.column('sensor_id', width=120, anchor='center')
        self.tree.column('value', width=100, anchor='center')
        self.tree.column('unit', width=80, anchor='center')
        self.tree.column('timestamp', width=180, anchor='center')
        self.tree.column('avg_1h', width=100, anchor='center')
        self.tree.column('avg_12h', width=100, anchor='center')

        # Add scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Grid layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        # Configure grid weights
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Server stopped")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=2, column=0, sticky="ew")

    def start_server(self):
        """Start the server"""
        try:
            port = int(self.port_entry.get())
            self.server = NetworkServer(port=port, message_queue=self.message_queue)
            self.server_thread = threading.Thread(target=self.server.start, daemon=True)
            self.running = True
            self.server_thread.start()

            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.status_var.set(f"Server listening on port {port}")

        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")

    def stop_server(self):
        """Stop the server"""
        self.running = False
        if self.server:
            # Proper server shutdown would need to be implemented
            pass

        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_var.set("Server stopped")

    def check_messages(self):
        """Check for messages from server"""
        try:
            while True:
                msg_type, msg = self.message_queue.get_nowait()
                if msg_type == "sensor_data":
                    self.history.append({
                        'sensor_id': msg['sensor_id'],
                        'value': float(msg['value']),
                        'timestamp': datetime.fromisoformat(msg['timestamp'])
                    })
                    self.update_sensor(msg)
                elif msg_type == "error":
                    self.status_var.set(f"Error: {msg}")
        except queue.Empty:
            pass

        self.root.after(100, self.check_messages)

    def calculate_averages(self, sensor_id):
        """Calculate averages for given sensor"""
        now = datetime.now()
        one_hour_ago = now - timedelta(hours=1)
        twelve_hours_ago = now - timedelta(hours=12)

        values_1h = []
        values_12h = []

        for entry in self.history:
            if entry['sensor_id'] == sensor_id:
                if entry['timestamp'] >= one_hour_ago:
                    values_1h.append(entry['value'])
                if entry['timestamp'] >= twelve_hours_ago:
                    values_12h.append(entry['value'])

        avg_1h = sum(values_1h) / len(values_1h) if values_1h else 0
        avg_12h = sum(values_12h) / len(values_12h) if values_12h else 0

        return round(avg_1h, 2), round(avg_12h, 2)

    def update_sensor(self, sensor_data):
        """Update sensor data"""
        sensor_id = sensor_data['sensor_id']
        avg_1h, avg_12h = self.calculate_averages(sensor_id)

        self.sensors[sensor_id] = {
            'value': f"{float(sensor_data['value']):.2f}",
            'unit': sensor_data['unit'],
            'timestamp': datetime.fromisoformat(sensor_data['timestamp']).strftime('%Y-%m-%d %H:%M:%S'),
            'avg_1h': f"{avg_1h:.2f}",
            'avg_12h': f"{avg_12h:.2f}"
        }

    def update_sensor_data(self):
        """Update the table with current sensor data"""
        # Clear current data
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Add sensor data to table
        for sensor_id, data in self.sensors.items():
            self.tree.insert('', 'end', values=(
                sensor_id,
                data['value'],
                data['unit'],
                data['timestamp'],
                data['avg_1h'],
                data['avg_12h']
            ))

        # Schedule next update
        self.root.after(1000, self.update_sensor_data)

    def on_close(self):
        """Handle window close"""
        self.stop_server()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ServerGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.minsize(1000, 500)  # Zwiększone okno dla dodatkowych kolumn
    root.mainloop()