import os
import time
from utils.db_utils import switch_to_root, connect_via_ssh, switch_to_enterprisedb, switch_to_server
from config import SERVER_CONFIG

def log_shell_output(shell, log_file_path):
    """
    Log all shell commands and their outputs to a local file.
    """
    print(f"Logging shell commands and outputs to {log_file_path}")

    # Ensure the directory exists
    directory = os.path.dirname(log_file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Directory {directory} created.")

    with open(log_file_path, 'a') as log_file:
        while True:
            if shell.recv_ready():
                output = shell.recv(1024).decode()
                log_file.write(output)
                log_file.flush()
            time.sleep(0.5)
            if not shell.recv_ready():
                break

def setup_recovery_files(shell, base_path, log_file_path=None):
    """
    Create the recovery signal file and rename the standby signal file.
    """
    print("Setting up recovery files")
    shell.send(f"touch {base_path}/recovery.signal\n")
    if log_file_path:
        log_shell_output(shell, log_file_path)
    time.sleep(1)
    shell.send(f"mv {base_path}/standby.signal {base_path}/standby.signalold\n")
    # mv /u01/edb/as15/data/standby.signalold /u01/edb/as15/data/standby.signal
    if log_file_path:
        log_shell_output(shell, log_file_path)
    time.sleep(1)
    
def edit_postgresql_conf(shell, base_path, recovery_time, log_file_path=None):
    """
    Update the recovery_target_time in postgresql.conf using sed.
    Handles both commented and uncommented lines.
    """
    print("Editing postgresql.conf to set recovery_target_time")
    command = (
        f"sed -i \"s/^#\\?recovery_target_time =.*/recovery_target_time = '{recovery_time}'/\" "
        f"{base_path}/postgresql.conf"
    )
    shell.send(command + '\n')
    if log_file_path:
        log_shell_output(shell, log_file_path)
    time.sleep(2)
    
    command = (
        f"sed -i \"s/^#\\?port =.*/port = 5444/\" "
        f"{base_path}/postgresql.conf"
    )
    shell.send(command + '\n')
    if log_file_path:
        log_shell_output(shell, log_file_path)
    time.sleep(2) 

def edit_postgresql_conf_for_wal(shell, base_path, wal_file_name, log_file_path=None):
    """
    Update the recovery_target_lsn in postgresql.conf using sed.
    Handles both commented and uncommented lines.
    """
    print("Editing postgresql.conf for WAL recovery")
    command = (
        f"sed -i \"s/^#\\?recovery_target_lsn =.*/recovery_target_lsn = '{wal_file_name}'/\" "
        f"{base_path}/postgresql.conf"
    )
    shell.send(command + '\n')
    if log_file_path:
        log_shell_output(shell, log_file_path)
    time.sleep(2)
    
    command = (
        f"sed -i \"s/^#\\?port =.*/port = 5444/\" "
        f"{base_path}/postgresql.conf"
    )
    shell.send(command + '\n')
    if log_file_path:
        log_shell_output(shell, log_file_path)
    time.sleep(2)  

def save_postgresql_conf_to_file(shell, base_path, local_file_path, log_file_path=None):
    """
    Read the postgresql.conf file and save it to a local text file.
    Optionally logs shell commands and their outputs.
    """
    print("Reading postgresql.conf and saving it to a local file")

    # Ensure the directory exists
    directory = os.path.dirname(local_file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Directory {directory} created.")

    # Command to display the content of postgresql.conf
    shell.send(f"cat {base_path}/postgresql.conf\n")
    if log_file_path:
        log_shell_output(shell, log_file_path)
    time.sleep(5)

    # Receive the content from the shell output
    output = shell.recv(1024).decode()

    # Save the content to the local file
    with open(local_file_path, 'w') as file:
        file.write(output)

    print(f"postgresql.conf saved to {local_file_path}")

def restart_postgresql_service(shell, log_file_path=None):
    """
    Restart the PostgreSQL service.
    """
    print("Restarting PostgreSQL service")
    restart_command = "systemctl restart edb-as-15.service"
    shell.send(restart_command + '\n')
    if log_file_path:
        log_shell_output(shell, log_file_path)
    time.sleep(5)
    
# def get_the_path(recovery_database):
#     try:
#         # Check if the recovery_database exists as a key in the config dictionary
#         if recovery_database in CONFIG_FILE_PATH_CONFIG:
#             return CONFIG_FILE_PATH_CONFIG[recovery_database]
#         else:
#             raise ValueError(f"No path found for recovery database: {recovery_database}")
#     except Exception as e:
#         print(f"Error in get_the_path: {str(e)}")
#         raise

# def get_the_path(recovery_database, recovery_host):
#     try:
#         # Iterate through all database configurations in SERVER_CONFIG
#         for db_config in SERVER_CONFIG.values():
#             # Check if the recovery_database exists as a key in the CONFIG_FILE_PATH_CONFIG of the current db_config
#             if recovery_database in db_config.get("CONFIG_FILE_PATH_CONFIG", {}):
#                 return db_config["CONFIG_FILE_PATH_CONFIG"][recovery_database]
        
#         # If the recovery_database wasn't found in any config, raise an error
#         raise ValueError(f"No path found for recovery database: {recovery_database}")

#     except Exception as e:
#         print(f"Error in get_the_path: {str(e)}")
#         raise

def get_the_path(recovery_port):
    try:
        # Iterate through all database configurations in SERVER_CONFIG
        for db_config in SERVER_CONFIG.values():
            print(db_config["port"])
            # Check if the recovery_host matches the pg_host of the current db_config
            if db_config["port"] == recovery_port:
                print(db_config["port"])
                # If the recovery_database exists as a key in the CONFIG_FILE_PATH_CONFIG
                return db_config.get("base_path")
        
        # If no matching recovery_database is found in any config for the recovery_host, raise an error
        raise ValueError(f"No path found for recovery port: {recovery_port}")

    except Exception as e:
        print(f"Error in get_the_path: {str(e)}")
        raise

def run_full_process_with_recovery_time(recovery_time, ssh_host, recovery_host, ssh_user, ssh_password,recovery_port):
    try:
        print(f"Executing run_full_process_with_recovery_time with host={ssh_host}, user={ssh_user}, recovery_time={recovery_time}")

        base_path = get_the_path(recovery_port)
        # base_path = "/u01/edb/as15/data"
        # f"sed -i \"s/^\\(recovery_target_time =.*\\)/#\\1/\" /u01/edb/as15/data/postgresql.conf"

        # Connect to the server via SSH
        ssh = connect_via_ssh(ssh_host, ssh_user, ssh_password)
        print("SSH connection established.")
        shell = ssh.invoke_shell()

        # # Log file path
        # log_file_path = os.path.join(PATH_CONFIG["blueprints_directory"], "shell_commands.log")

        # Switch to root and then to the EnterpriseDB user
        switch_to_root(shell, ssh_password)
        print("Switched to root user.")

        switch_to_enterprisedb(shell)
        print("Switched to enterprisedb user.")

        # switch_to_server(shell)
        switch_to_server(shell, recovery_host)

        # Create the recovery file
        setup_recovery_files(shell, base_path)

        # Edit the postgresql.conf file with the recovery time
        edit_postgresql_conf(shell, base_path, recovery_time)

        # Restart the PostgreSQL service to apply changes
        restart_postgresql_service(shell)

        # Close SSH session
        shell.close()
        ssh.close()
        print("SSH connection closed.")

        return {"status": "success", "message": "Recovery process completed successfully."}

    except Exception as e:
        print(f"Error in run_full_process_with_recovery_time: {str(e)}")
        return {"status": "error", "message": str(e)}

def run_full_process_with_wal_file(wal_file_name, ssh_host, recovery_host, ssh_user, ssh_password, recovery_port):
    try:
        print(f"Executing run_full_process_with_wal_file with host={ssh_host}, user={ssh_user}, wal_file_name={wal_file_name}")

        # Connect to the server via SSH
        ssh = connect_via_ssh(ssh_host, ssh_user, ssh_password)
        print("SSH connection established.")
        shell = ssh.invoke_shell()
        
        base_path = get_the_path(recovery_port)

        # Log file path
        # log_file_path = os.path.join(PATH_CONFIG["blueprints_directory"], "shell_commands.log")

        # Switch to root and then to the EnterpriseDB user
        switch_to_root(shell, ssh_password)
        print("Switched to root user.")

        switch_to_enterprisedb(shell)
        print("Switched to enterprisedb user.")
        
        switch_to_server(shell, recovery_host)

        # Create the recovery file
        setup_recovery_files(shell, base_path)

        # Edit the postgresql.conf file for WAL recovery
        edit_postgresql_conf_for_wal(shell, base_path, wal_file_name)
        
        # Restart the PostgreSQL service to apply changes
        restart_postgresql_service(shell)

        # Close SSH session
        shell.close()
        ssh.close()
        print("SSH connection closed.")

        return {"status": "success", "message": "WAL recovery process completed successfully."}

    except Exception as e:
        print(f"Error in run_full_process_with_wal_file: {str(e)}")
        return {"status": "error", "message": str(e)}
    
def switch_primary_database(ssh_host, ssh_user, ssh_password, recovery_host, recovery_port):
    try:
        # print(f"Executing run_full_process_with_wal_file with host={ssh_host}, user={ssh_user}, wal_file_name={wal_file_name}")

        # Connect to the server via SSH
        ssh = connect_via_ssh(ssh_host, ssh_user, ssh_password)
        print("SSH connection established.")
        shell = ssh.invoke_shell()
        
        base_path = get_the_path(recovery_port)

        # Log file path
        # log_file_path = os.path.join(PATH_CONFIG["blueprints_directory"], "shell_commands.log")

        # Switch to root and then to the EnterpriseDB user
        switch_to_root(shell, ssh_password)
        print("Switched to root user.")

        switch_to_enterprisedb(shell)
        print("Switched to enterprisedb user.")
        
        switch_to_server(shell, recovery_host)
        
        # Run the 'pg_ctl promote' command to promote the secondary to primary
        promote_command = f"/usr/edb/as15/bin/pg_ctl promote -D {base_path}"
        shell.send(f"{promote_command}\n")
        time.sleep(5)
        
        # Restart the PostgreSQL service to apply changes
        # restart_postgresql_service(shell)

        # Close SSH session
        shell.close()
        ssh.close()
        print("SSH connection closed.")

        return {"status": "success", "message": "Database Switching process completed successfully."}

    except Exception as e:
        print(f"Error in run_full_process_with_wal_file: {str(e)}")
        return {"status": "error", "message": str(e)}