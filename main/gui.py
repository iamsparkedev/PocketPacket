
# All UI logic is here; backend logic is imported from core modules.

import customtkinter as ctk
from tkinter import messagebox

# Import core functions
from core.sendpacket import send_packet
from core.utils import parse_headers, format_response
from core.history import add_to_history, get_history

ctk.set_appearance_mode("System")  # Options: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")

class PocketPacketApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PocketPacket")
        self.geometry("800x800")
        self.resizable(False, False)

        # --- Sidebar for navigation ---
        self.sidebar = ctk.CTkFrame(self, width=150)
        self.sidebar.pack(side="left", fill="y")

        self.tab_var = ctk.StringVar(value="Send")
        self.send_btn = ctk.CTkButton(self.sidebar, text="Send", command=lambda: self.show_tab("Send"))
        self.send_btn.pack(pady=20, padx=10, fill="x")
        self.history_btn = ctk.CTkButton(self.sidebar, text="History", command=lambda: self.show_tab("History"))
        self.history_btn.pack(pady=10, padx=10, fill="x")

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

        # --- Headers Input ---
        headers_label = ctk.CTkLabel(self.content, text="Headers (Python dict):")
        headers_label.grid(row=2, column=0, sticky="nw", padx=10)
        self.headers_text = ctk.CTkTextbox(self.content, height=80, width=400)
        self.headers_text.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        # --- Body Input ---
        body_label = ctk.CTkLabel(self.content, text="Body:")
        body_label.grid(row=3, column=0, sticky="nw", padx=10)
        self.body_text = ctk.CTkTextbox(self.content, height=120, width=400)
        self.body_text.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

        # --- Send Button ---
        send_btn = ctk.CTkButton(self.content, text="Send Packet", command=self.send_packet)
        send_btn.grid(row=4, column=1, sticky="e", padx=10, pady=10)

        # --- Response Viewer ---
        response_label = ctk.CTkLabel(self.content, text="Response:")
        response_label.grid(row=5, column=0, sticky="nw", padx=10)
        self.response_text = ctk.CTkTextbox(self.content, height=200, width=600)
        self.response_text.grid(row=5, column=1, padx=10, pady=5, sticky="nsew")

    def send_packet(self):
        # --- Gather Input Data ---
        url = self.url_entry.get()
        method = self.method_var.get()
        headers = self.headers_text.get("1.0", "end").strip()
        body = self.body_text.get("1.0", "end").strip()

        # --- Parse Headers ---
        try:
            headers_dict = parse_headers(headers)
        except ValueError as e:
            messagebox.showerror("Invalid Headers", str(e))
            return

        # --- Send HTTP Request ---
        status, resp = send_packet(url, method, headers_dict, body)
        self.response_text.delete("1.0", "end")
        if status is not None:
            formatted = format_response(resp)
            self.response_text.insert("end", f"Status: {status}\n\n{formatted}")
            add_to_history({
                "url": url,
                "method": method,
                "headers": headers_dict,
                "body": body,
                "status": status,
                "response": formatted
            })
        else:
            self.response_text.insert("end", f"Error: {resp}")

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
                history_list.insert("end", f"Headers: {entry['headers']}\nBody: {entry['body']}\nResponse: {entry['response']}\n{'-'*60}\n")
        else:
            history_list.insert("end", "No history yet.")

# --- Run the App ---
if __name__ == "__main__":
    app = PocketPacketApp()
    app.mainloop()
