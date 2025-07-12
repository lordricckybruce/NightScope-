NightScope

NightScope is a fast, stealthy port scanner project integrating 
a high-performance Go backend scanner with a Python GUI frontend.
I used Go language for its backend scanning due  
1. High performance and speed scanning due to it's efficient concurrency support
   allowing scanner to send and handle thousands of network packets with heavy resource usage.
2. Reduced Detection Risks due to it's speed with raw socket allow the scanner 
   to send SYN packets stealthily, helping to by pass or reduce detection by firewalLs, IPS or IDS systems
Summary:
while go handles intensive stealthy network scanning effieciently 
python offers a flexible, user friendly interface with powerful UI libraries and resources

---

## Project Structure
NightScope/
├── go_scanner/                    # 🔧 Go-based fast scanner
│   ├── scanner.go                 # Already done
│   └── run.sh                     # Optional Go build helper

├── python_gui/                    # 🖥️ GUI interface (already works)
│   ├── gui_nightscope.py
│   ├── requirements.txt
│   └── README.md

├── cli_interface/                # 🧪 New CLI interface
│   ├── ngsp.py                   # Python CLI frontend using: ngsp --scan <target>
│   └── README.md

├── output/                        # 📦 Output directory
│   ├── results.json
│   └── summary.txt

└── README.md                      # 📘 Master documentation
 

#Operational Mechanism 

1. Target Input : Have a target.
2. Stealthy Scanning for open ports(Backend): Performs a TCP SYN scan
3. Port Probing: Utilizing Go's Lightweight goroutines, the scanner probes
   multiple ports.
4. Real-Time Output: Scanner reports open ports.
5. Result Processing: Python GUI collects scan results, displays detailed output.
   and a summarized list.
6. Exports And Reporting: Saves result as JSON files and as text files for further analysis.
