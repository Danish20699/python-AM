import sys
import os
import paramiko

def check_single_vm_uptime(hostname, username, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print(f"Connecting to [{hostname}] as '{username}'...")
        client.connect(
            hostname=hostname,
            port=22,
            username=username,
            password=password,
            timeout=10
        )

        stdin, stdout, stderr = client.exec_command('uptime')
        output = stdout.read().decode('utf-8').strip()
        error = stderr.read().decode('utf-8').strip()

        if output:
            print(f"\n[SUCCESS] 🟢 [{hostname}] Uptime Info:")
            print(f"--> {output}\n")
        if error:
            print(f"\n[ERROR] 🔴 [{hostname}]: {error}\n", file=sys.stderr)

    except paramiko.AuthenticationException:
        print(f"\n[FAILED] 🔴 Authentication error for user '{username}'. Check password.", file=sys.stderr)
    except Exception as e:
        print(f"\n[FAILED] 🔴 Could not connect to {hostname}: {e}", file=sys.stderr)
    finally:
        client.close()

def main():
    if len(sys.argv) < 3:
        print("Usage: python 32-check-uptime-on-single-vm.py <hostname> <username>")
        print("Example: python 32-check-uptime-on-single-vm.py 127.0.0.1 danis")
        sys.exit(1)

    host = sys.argv[1]
    user = sys.argv[2]
    pwd = os.getenv("SSH_PASSWORD", "danishh")

    check_single_vm_uptime(host, user, pwd)

if __name__ == "__main__":
    main()