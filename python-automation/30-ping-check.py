import subprocess
import platform

servers = [
    "192.168.1.1",
    "google.com",
    "yahoo.com",
    "10.0.0.1",
    "8.8.8.8"
]

# Use '-n' on Windows, '-c' on Linux/Mac
ping_flag = "-n" if platform.system().lower() == "windows" else "-c"

print("Starting the script to check all servers...\n")

for server in servers:
    result = subprocess.run(["ping", ping_flag, "2", server], capture_output=True, text=True)

    # returncode 0 means ping is successful
    if result.returncode == 0:
        print(f"🟢 {server} is UP!")
    else:
        print(f"🔴 {server} is DOWN!!!")