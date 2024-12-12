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
        # If password is provided for sudo, use it in the sudo command
        if password and command.startswith('sudo'):
            command = f'{password} | {command}'

        stdin, stdout, stderr = ssh_client.exec_command(command)

        # Read the output and error
        output = stdout.read().decode()
        error = stderr.read().decode()

        if output:
            print(f"Command output: {output}")
        if error:
            print(f"Command error: {error}")

        return output, error
    except Exception as e:
        print(f"Error executing command: {str(e)}")
        return "", str(e)
