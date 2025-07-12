import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import subprocess
import threading
import re
import time
import json
import os

PORT_SERVICES = {
    80: "HTTP",
    443: "HTTPS",
    21: "FTP",
    22: "SSH",
    25: "SMTP",
    53: "DNS",
    110: "POP3",
    143: "IMAP",
    3306: "MySQL",
    8080: "HTTP-Alt",
    5900: "VNC"
}

class NightScopeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NightScope - Stealth Port Scanner")
        self.root.configure(bg="#0d0d1a")
        self.root.geometry("850x660")

        if os.path.exists("nightscope.ico"):
            self.root.iconbitmap("nightscope.ico")

        self.mode = tk.StringVar(value="GUI")
        self.setup_widgets()

    def setup_widgets(self):
        header = tk.Label(self.root, text="NightScope Scanner", font=("Consolas", 20, "bold"), fg="cyan", bg="#0d0d1a")
        header.pack(pady=10)

        mode_frame = tk.Frame(self.root, bg="#0d0d1a")
        mode_frame.pack()
        tk.Radiobutton(mode_frame, text="GUI Mode (Go Scanner)", variable=self.mode, value="GUI", fg="white", bg="#0d0d1a").pack(side=tk.LEFT)
        tk.Radiobutton(mode_frame, text="CLI Mode (Python Scanner)", variable=self.mode, value="CLI", fg="white", bg="#0d0d1a").pack(side=tk.LEFT)

        tk.Label(self.root, text="Target IP or DNS:", fg="lime", bg="#0d0d1a").pack(pady=2)
        self.target_entry = tk.Entry(self.root, width=50, bg="black", fg="cyan")
        self.target_entry.pack(pady=5)

        tk.Label(self.root, text="Optional: Max Port (1-65535, Default 1000):", fg="lime", bg="#0d0d1a").pack(pady=2)
        self.port_entry = tk.Entry(self.root, width=20, bg="black", fg="cyan")
        self.port_entry.pack(pady=5)

        self.scan_btn = tk.Button(self.root, text="Start Scan", command=self.start_scan, bg="blue", fg="white", font=("Consolas", 12, "bold"))
        self.scan_btn.pack(pady=10)

        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=300, mode="indeterminate")
        self.progress.pack(pady=5)

        self.output_box = scrolledtext.ScrolledText(self.root, width=100, height=15, bg="black", fg="lime")
        self.output_box.pack(padx=10, pady=10)

        tk.Label(self.root, text="Open Ports Summary:", fg="lime", bg="#0d0d1a").pack()
        self.summary_box = tk.Text(self.root, height=5, bg="black", fg="green")
        self.summary_box.pack(fill="both", padx=10)

        frame = tk.Frame(self.root, bg="#0d0d1a")
        frame.pack(pady=5)
        self.save_btn = tk.Button(frame, text="Save Results", command=self.save_results, bg="gray", fg="white")
        self.save_btn.pack(side=tk.LEFT, padx=5)
        about_btn = tk.Button(frame, text="About", command=self.show_about, bg="darkblue", fg="white")
        about_btn.pack(side=tk.LEFT, padx=5)

    def start_scan(self):
        target = self.target_entry.get().strip()
        port_limit = self.port_entry.get().strip()

        if not target:
            messagebox.showwarning("Input Error", "Please enter a target IP or domain.")
            return

        max_port = port_limit if port_limit.isdigit() and 1 <= int(port_limit) <= 65535 else "1000"

        if self.mode.get() == "CLI":
            self.launch_cli_mode(target, max_port)
            return

        self.start_time = time.time()
        self.output_box.delete("1.0", tk.END)
        self.summary_box.delete("1.0", tk.END)
        self.progress.start()
        self.scan_btn.config(state=tk.DISABLED)

        thread = threading.Thread(target=self.run_go_scan, args=(target, max_port))
        thread.start()

    def launch_cli_mode(self, target, max_port):
        try:
            cmd = f"python3 ../cli_interface/ngsp.py --scan {target} --max {max_port}"
            subprocess.Popen(["x-terminal-emulator", "-e", cmd])
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("CLI Error", f"Failed to launch CLI mode: {str(e)}")

    def run_go_scan(self, target, max_port):
        open_ports = []
        ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

        try:
            scanner_path = "../go_scanner/scanner"
            if not os.path.exists(scanner_path):
                self.output_box.insert(tk.END, f"Go scanner not found at {scanner_path}\n")
                return

            process = subprocess.Popen(
                [scanner_path, target, max_port],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            for line in process.stdout:
                decoded = line.decode("utf-8").strip()
                clean_line = ansi_escape.sub('', decoded)
                self.output_box.insert(tk.END, decoded + "\n")
                self.output_box.see(tk.END)

                match = re.search(r"\[OPEN\] Port (\d+)", clean_line)
                if match:
                    port = int(match.group(1))
                    if port not in open_ports:
                        open_ports.append(port)

            self.build_summary(open_ports)

        except Exception as e:
            self.output_box.insert(tk.END, f"Error: {str(e)}\n")
        finally:
            elapsed = round(time.time() - self.start_time, 2)
            self.output_box.insert(tk.END, f"\n[✔] Scan completed in {elapsed} seconds\n")
            self.progress.stop()
            self.scan_btn.config(state=tk.NORMAL)
            self.export_to_json(open_ports)

    def build_summary(self, ports):
        if not ports:
            self.summary_box.insert(tk.END, "No open ports found.\n")
            return
        for port in sorted(ports):
            service = PORT_SERVICES.get(port, "Unknown")
            self.summary_box.insert(tk.END, f"Port {port} ➜ {service}\n")

    def save_results(self):
        try:
            os.makedirs("../output", exist_ok=True)
            with open("../output/summary.txt", "w") as f:
                f.write("NightScope Scan Results\n")
                f.write("Target: " + self.target_entry.get().strip() + "\n\n")
                f.write("--- Detailed Output ---\n")
                f.write(self.output_box.get("1.0", tk.END))
                f.write("\n--- Open Ports Summary ---\n")
                f.write(self.summary_box.get("1.0", tk.END))
            messagebox.showinfo("Saved", "Results saved to output/summary.txt and summary.json")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save results: {str(e)}")

    def export_to_json(self, ports):
        data = {
            "target": self.target_entry.get().strip(),
            "open_ports": [{"port": p, "service": PORT_SERVICES.get(p, "Unknown")} for p in ports],
            "timestamp": time.ctime(),
        }
        try:
            with open("../output/summary.json", "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print("Failed to export JSON:", e)

    def show_about(self):
        messagebox.showinfo("About NightScope", "NightScope\nVersion 1.0\nAuthor: Alexander Ireka\nGUI by Mr. Kulian\n\nA stealthy, multi-language port scanner built using Go and Python.")

if __name__ == "__main__":
    root = tk.Tk()
    app = NightScopeApp(root)
    root.mainloop()
