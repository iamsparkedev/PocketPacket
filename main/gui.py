
# All UI logic is here; backend logic is imported from core modules.

import customtkinter as ctk
from tkinter import messagebox

# Import core functions
from core.sendpacket import send_packet
from core.utils import parse_headers, format_response, format_headers
from core.history import add_to_history, get_history

ctk.set_appearance_mode("System")  # Options: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")

class PocketPacketApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PocketPacket")
        self.geometry("800x800")
        self.resizable(False, False)


        self.sidebar = ctk.CTkFrame(self, width=150)
        self.sidebar.pack(side="left", fill="y")

        self.tab_var = ctk.StringVar(value="Send")
        self.send_btn = ctk.CTkButton(self.sidebar, text="Send", command=lambda: self.show_tab("Send"))
        self.send_btn.pack(pady=5, padx=10, fill="x")
        self.history_btn = ctk.CTkButton(self.sidebar, text="History", command=lambda: self.show_tab("History"))
        self.history_btn.pack(pady=5, padx=10, fill="x")

        # --- Main content area ---
        self.content = ctk.CTkFrame(self)
        self.content.pack(side="left", fill="both", expand=True)

        # --- Tabs ---
        self.tabs = {
            "Send": self.build_send_tab,
            "History": self.build_history_tab
        }
        self.current_tab = None
        self.show_tab("Send")

    def show_tab(self, tab_name):
        # Clear current content
        for widget in self.content.winfo_children():
            widget.destroy()
        self.current_tab = tab_name
        self.tabs[tab_name]()

    def build_send_tab(self):
        # --- Make right column expandable ---
        self.content.grid_columnconfigure(1, weight=1)

        # --- URL Input ---
        url_label = ctk.CTkLabel(self.content, text="URL:")
        url_label.grid(row=0, column=0, sticky="w", padx=10, pady=10)
        self.url_entry = ctk.CTkEntry(self.content, width=400)
        self.url_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        # --- Method Selection ---
        method_label = ctk.CTkLabel(self.content, text="Method:")
        method_label.grid(row=1, column=0, sticky="w", padx=10)
        self.method_var = ctk.StringVar(value="GET")
        self.method_menu = ctk.CTkComboBox(self.content, variable=self.method_var, values=["GET", "POST", "PUT", "DELETE"], width=120)
        self.method_menu.grid(row=1, column=1, sticky="w", padx=10)

        # --- Number of Packets Entry with Plus/Minus Buttons ---
        packets_label = ctk.CTkLabel(self.content, text="Number of Packets:")
        packets_label.grid(row=2, column=0, sticky="w", padx=10)
        packets_frame = ctk.CTkFrame(self.content)
        packets_frame.grid(row=2, column=1, sticky="w", padx=10)
        self.packets_entry = ctk.CTkEntry(packets_frame, width=60)
        self.packets_entry.pack(side="left", padx=(0,5))
        self.packets_entry.insert(0, "1")
        def increment_packets():
            try:
                val = int(self.packets_entry.get())
                self.packets_entry.delete(0, "end")
                self.packets_entry.insert(0, str(val+1))
            except:
                self.packets_entry.delete(0, "end")
                self.packets_entry.insert(0, "1")
        def decrement_packets():
            try:
                val = int(self.packets_entry.get())
                if val > 1:
                    self.packets_entry.delete(0, "end")
                    self.packets_entry.insert(0, str(val-1))
            except:
                self.packets_entry.delete(0, "end")
                self.packets_entry.insert(0, "1")
        plus_btn = ctk.CTkButton(packets_frame, text="+", width=30, command=increment_packets)
        plus_btn.pack(side="left")
        minus_btn = ctk.CTkButton(packets_frame, text="-", width=30, command=decrement_packets)
        minus_btn.pack(side="left", padx=(5,0))

        # --- Headers Input ---
        headers_label = ctk.CTkLabel(self.content, text="Headers (Python dict or JSON):")
        headers_label.grid(row=3, column=0, sticky="nw", padx=10)
        self.headers_text = ctk.CTkTextbox(self.content, height=80, width=400)
        self.headers_text.grid(row=3, column=1, padx=10, pady=5, sticky="ew")
        # Add placeholder suggestion for headers
        self.headers_text.insert("1.0", '{"Content-Type": "application/json"}')

        # --- Body Input ---
        body_label = ctk.CTkLabel(self.content, text="Body:")
        body_label.grid(row=4, column=0, sticky="nw", padx=10)
        self.body_text = ctk.CTkTextbox(self.content, height=120, width=400)
        self.body_text.grid(row=4, column=1, padx=10, pady=5, sticky="ew")
        # Add placeholder suggestion for body
        self.body_text.insert("1.0", '{"username": "user", "password": "pass"}')

        # --- Send Button ---
        send_btn = ctk.CTkButton(self.content, text="Send Packet", command=self.send_packet)
        send_btn.grid(row=5, column=1, sticky="e", padx=10, pady=10)

        # --- Response Viewer ---
        response_label = ctk.CTkLabel(self.content, text="Response:")
        response_label.grid(row=6, column=0, sticky="nw", padx=10)
        self.response_text = ctk.CTkTextbox(self.content, height=200, width=600)
        self.response_text.grid(row=6, column=1, padx=10, pady=5, sticky="nsew")

    def send_packet(self):
        # --- Gather Input Data ---
        url = self.url_entry.get()
        method = self.method_var.get()
        headers = self.headers_text.get("1.0", "end").strip()
        body = self.body_text.get("1.0", "end").strip()
        try:
            num_packets = int(self.packets_entry.get())
            if num_packets < 1:
                raise ValueError
        except Exception:
            messagebox.showerror("Invalid Number", "Number of packets must be a positive integer.")
            return

        # --- Parse Headers ---
        try:
            headers_dict = parse_headers(headers)
        except ValueError as e:
            messagebox.showerror("Invalid Headers", str(e))
            return

        self.response_text.delete("1.0", "end")
        for i in range(num_packets):
            status, resp_headers, resp_body = send_packet(url, method, headers_dict, body)
            if status is not None:
                formatted_headers = format_headers(resp_headers)
                formatted_body = format_response(resp_body)
                output = f"Packet {i+1} - Status: {status}\nHeaders:\n{formatted_headers}\n\nBody:\n{formatted_body}\n{'-'*40}\n"
                self.response_text.insert("end", output)
                add_to_history({
                    "url": url,
                    "method": method,
                    "headers": headers_dict,
                    "body": body,
                    "status": status,
                    "resp_headers": formatted_headers,
                    "resp_body": formatted_body
                })
            else:
                self.response_text.insert("end", f"Packet {i+1} - Error: {resp_body}\n{'-'*40}\n")

    def build_history_tab(self):
        # --- History Tab Layout (using grid) ---
        history_label = ctk.CTkLabel(self.content, text="Request History:", font=("Arial", 16))
        history_label.grid(row=0, column=0, sticky="w", padx=10, pady=10)
        history_list = ctk.CTkTextbox(self.content, height=600, width=600)
        history_list.grid(row=1, column=0, padx=10, pady=10)
        entries = get_history()
        if entries:
            for entry in entries:
                history_list.insert("end", f"{entry['method']} {entry['url']} | Status: {entry['status']}\n")
                history_list.insert("end", f"Request Headers: {entry['headers']}\nRequest Body: {entry['body']}\n")
                history_list.insert("end", f"Response Headers:\n{entry['resp_headers']}\nResponse Body:\n{entry['resp_body']}\n{'-'*60}\n")
        else:
            history_list.insert("end", "No history yet.")

# --- Run the App ---
if __name__ == "__main__":
    app = PocketPacketApp()
    app.mainloop()
