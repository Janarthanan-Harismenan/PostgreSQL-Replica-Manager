import paramiko

def ssh_connect_and_execute(host, username, password, command):
    print(f"Attempting SSH connection to {host} as {username}")

    try:
        # Establish SSH connection
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # Automatically add host key
        print("SSH client configured. Connecting...")
        ssh_client.connect(host, username=username, password=password)
        print(f"Successfully connected to {host}")

        # Execute the command
        print(f"Executing command: {command}")
        stdin, stdout, stderr = ssh_client.exec_command(command)

        # Read the output and error
        output = stdout.read().decode()
        error = stderr.read().decode()

        if output:
            print(f"Command output: {output}")
        if error:
            print(f"Command error: {error}")

        ssh_client.close()
        print("SSH connection closed.")

        return output, error
    except Exception as e:
        print(f"Error during SSH connection or command execution: {str(e)}")
        return str(e), ""
