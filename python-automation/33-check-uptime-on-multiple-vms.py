import argparse
import paramiko
import sys
import os

def get_remote_uptime(hostname, port, username, password):
    # Initialize the SSH client
    client = paramiko.SSHClient()
    
    # Automatically add unknown host keys
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # Connect using only the password
        client.connect(hostname, port=port, username=username, password=password)
            
        # Execute the uptime command
        stdin, stdout, stderr = client.exec_command('uptime')
        
        # Decode the byte stream to string
        output = stdout.read().decode('utf-8').strip()
        error = stderr.read().decode('utf-8').strip()
        
        if output:
            print(f"[{hostname}] {output}")
        if error:
            print(f"[{hostname}] Error: {error}", file=sys.stderr)
            
    except paramiko.AuthenticationException:
        print(f"[{hostname}] Authentication failed for {username}. Check your SSH_PASSWORD.")
    except paramiko.SSHException as ssh_err:
        print(f"[{hostname}] SSH error occurred: {ssh_err}")
    except Exception as e:
        print(f"[{hostname}] Connection error: {e}")
    finally:
        # Ensure the connection is closed
        client.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run 'uptime' on multiple remote servers (password-only via env var).")
    
    # CHANGED: Now accepts MULTIPLE hostnames
    parser.add_argument('hostnames', nargs='+', help='One or more hostnames or IP addresses')
    
    # Required/Optional arguments
    parser.add_argument('-u', '--user', required=True, help='SSH username')
    parser.add_argument('--port', type=int, default=22, help='SSH port (default: 22)')
    
    args = parser.parse_args()
    
    # Read the password from the environment variable
    env_password = os.getenv('SSH_PASSWORD')
    
    # Ensure the password environment variable is set
    if not env_password:
        print("Error: You must set the 'SSH_PASSWORD' environment variable.", file=sys.stderr)
        sys.exit(1)
    
    # NEW: FOR LOOP to process each hostname
    for hostname in args.hostnames:
        get_remote_uptime(hostname, args.port, args.user, env_password)