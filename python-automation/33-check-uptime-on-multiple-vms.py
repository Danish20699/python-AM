import sys
import os
import paramiko

def check_vm_uptime(ip, username, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(
            hostname=ip,
            port=22,
            username=username,
            password=password,
            timeout=5
        )
        stdin, stdout, stderr = client.exec_command('uptime')
        output = stdout.read().decode('utf-8').strip()
        print(f"[{ip:<15}] ?? {output}")

    except paramiko.AuthenticationException:
        print(f"[{ip:<15}] ?? Authentication Failed")
    except Exception as e:
        print(f"[{ip:<15}] ?? Unreachable ({e})")
    finally:
        client.close()

def main():
    if len(sys.argv) < 3:
        print("Usage: python 33-check-uptime-on-multiple-vms.py <username> <ip1> <ip2> ...")
        print("Example: python 33-check-uptime-on-multiple-vms.py danis 127.0.0.1 192.168.1.50")
        sys.exit(1)

    username = sys.argv[1]
    vm_ips = sys.argv[2:]
    password = os.getenv("SSH_PASSWORD", "danishh")

    print(f"\n{'='*60}")
    print(f"  ?? Checking Uptime on {len(vm_ips)} Virtual Machine(s)")
    print(f"{'='*60}\n")

    for ip in vm_ips:
        check_vm_uptime(ip, username, password)

    print(f"\n{'='*60}\n")

if __name__ == "__main__":
    main()
