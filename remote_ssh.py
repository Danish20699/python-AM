import os
import paramiko

# Server Configuration (127.0.0.1 or your WSL IP)
SERVERS = ["127.0.0.1"]
USERNAME = "danis"
PASSWORD = "danishh"

# Commands to check full system health
COMMANDS = {
    "System Uptime & Load": "uptime",
    "Memory (RAM) Usage": "free -h",
    "Disk Space Usage": "df -h /"
}

def run_health_check(ip, username, password):
    print(f"\n{'='*55}")
    print(f"  🔍 Checking Health for Server: {ip}")
    print(f"{'='*55}")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(
            hostname=ip,
            port=22,
            username=username,
            password=password,
            timeout=10
        )
        print(f"[STATUS] Connected successfully to {ip}!\n")

        for title, cmd in COMMANDS.items():
            print(f"--- {title} (`{cmd}`) ---")
            stdin, stdout, stderr = client.exec_command(cmd)
            
            output = stdout.read().decode('utf-8').strip()
            error = stderr.read().decode('utf-8').strip()

            if output:
                print(output)
            if error:
                print(f"[ERROR] {error}")
            print()

    except Exception as e:
        print(f"[FAILED] Could not connect to {ip}: {e}")
    finally:
        client.close()

def main():
    for server_ip in SERVERS:
        run_health_check(server_ip, USERNAME, PASSWORD)

if __name__ == "__main__":
    main()