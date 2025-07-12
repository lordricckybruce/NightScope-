#!/usr/bin/env python3
import argparse
import subprocess
import re
import os
import json
from datetime import datetime

PORT_SERVICES = {
    80: "HTTP", 443: "HTTPS", 21: "FTP", 22: "SSH", 25: "SMTP",
    53: "DNS", 110: "POP3", 143: "IMAP", 3306: "MySQL", 8080: "HTTP-Alt", 5900: "VNC"
}

def color(text, code):
    return f"\033[{code}m{text}\033[0m"

def main():
    parser = argparse.ArgumentParser(description="NightScope CLI - Fast Stealth Scanner")
    parser.add_argument('--scan', metavar='TARGET', required=True, help='Target IP or domain')
    parser.add_argument('--max', metavar='PORT', default='65535', help='Max port (default: 65535)')
    args = parser.parse_args()

    target = args.scan
    max_port = args.max

    print(color(f"\n[+] Starting stealth scan on {target} up to port {max_port}", "34"))

    if not os.path.exists("../go_scanner/scanner"):
        print(color("[!] Go binary not found. Run build script or compile manually.", "31"))
        return

    process = subprocess.Popen(
        ["../go_scanner/scanner", target, max_port],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    open_ports = []
    for line in process.stdout:
        decoded = line.decode("utf-8").strip()
        print(decoded)
        match = re.search(r"\[OPEN\] Port (\d+)", decoded)
        if match:
            port = int(match.group(1))
            service = PORT_SERVICES.get(port, "Unknown")
            open_ports.append({"port": port, "service": service})

    print(color(f"\n[✔] Scan completed.", "34"))

    # Save JSON
    data = {
        "target": target,
        "open_ports": open_ports,
        "timestamp": datetime.now().isoformat()
    }

    os.makedirs("../output", exist_ok=True)
    with open("../output/summary.json", "w") as f:
        json.dump(data, f, indent=4)

    with open("../output/summary.txt", "w") as f:
        f.write(f"Scan result for: {target}\n")
        f.write(f"Total Open Ports: {len(open_ports)}\n")
        for item in open_ports:
            f.write(f"Port {item['port']} ➜ {item['service']}\n")

if __name__ == "__main__":
    main()
