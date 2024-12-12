import paramiko

def ssh_connect(host, username, password):
    """
    Establishes an SSH connection to the specified host.
    
    Args:
        host (str): The SSH server's IP or hostname.
        username (str): The SSH username.
        password (str): The SSH password.
    
    Returns:
        ssh_client (paramiko.SSHClient): The established SSH client object.
        error (str): Any error message encountered during the connection attempt.
    """
    print(f"Attempting SSH connection to {host} as {username}")

    try:
        # Create SSH client and set policies
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # Automatically add host key
        print("SSH client configured. Connecting...")

        # Connect to the SSH server
        ssh_client.connect(host, username=username, password=password)
        print(f"Successfully connected to {host}")

        return ssh_client, None
    except Exception as e:
        print(f"Error during SSH connection: {str(e)}")
        return None, str(e)
    
def ssh_execute_command(ssh_client, command, password=None):
    try:
        # Open an interactive shell
        channel = ssh_client.invoke_shell()
       
        # Wait for the shell to be ready
        while not channel.recv_ready():
            pass
       
        # Execute 'sudo -i'
        channel.send('sudo -i\n')
       
        # Wait for the password prompt
        while not channel.recv_ready():
            pass
        output = channel.recv(1024).decode()
        print(f"Initial output: {output}")
       
        # Check for the password prompt and send the password
        if "password" in output.lower() and password:
            channel.send(f"{password}\n")
       
        # Wait for the shell to be ready again
        while not channel.recv_ready():
            pass
        output = channel.recv(1024).decode()
        print(f"Output after password: {output}")
       
        # Send the actual command
        channel.send(f"{command}\n")
       
        # Wait for the command to execute and collect output
        while not channel.recv_ready():
            pass
        output = channel.recv(4096).decode()
       
        print(f"Command output: {output}")
        return output, None  # Return the command output
    except Exception as e:
        print(f"Error executing command: {str(e)}")
        return "", str(e)