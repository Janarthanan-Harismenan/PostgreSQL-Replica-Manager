import os
import shlex
import subprocess
from utils.db_utils import switch_to_root, connect_via_ssh
import time
<<<<<<< HEAD
import re
# def search_wal_files_for_keyword(ssh, keyword, number_of_files):
#     """
#     Searches WAL files for a specific keyword within a given time range on a remote server via SSH.
#     """
#     try:
#         if not keyword.strip():
#             raise ValueError("Keyword cannot be empty or whitespace.")

#         escaped_keyword = shlex.quote(keyword.strip())
#         base_path = "/usr/edb/as16/include/server/archive"
#         find_command = (
#             f'find {base_path} -type f '
#             f'-newermt "{starting_time}" ! -newermt "{ending_time}" '
#             f'-exec bash -c \'strings "{{}}" | grep -q {escaped_keyword} && echo "{{}}"\' \\;'
            
#         )

=======

# def search_wal_files_for_keyword(ssh, keyword, number_of_files):
#     """
#     Searches WAL files for a specific keyword within a given time range on a remote server via SSH.
#     """
#     try:
#         if not keyword.strip():
#             raise ValueError("Keyword cannot be empty or whitespace.")

#         escaped_keyword = shlex.quote(keyword.strip())
#         base_path = "/usr/edb/as16/include/server/archive"
#         find_command = (
#             f'find {base_path} -type f '
#             f'-newermt "{starting_time}" ! -newermt "{ending_time}" '
#             f'-exec bash -c \'strings "{{}}" | grep -q {escaped_keyword} && echo "{{}}"\' \\;'
            
#         )

>>>>>>> abc1743438d1fe7ad3b01f888d4a1fe37db4edb6
#         print(f"Executing command on remote server: {find_command}")

#         # Execute the command on the remote server
#         stdin, stdout, stderr = ssh.exec_command(find_command)
#         stdout_lines = stdout.readlines()
#         stderr_lines = stderr.readlines()

#         # Check for errors
#         if stderr_lines:
#             error_message = ''.join(stderr_lines)
#             print(f"Error occurred during remote search: {error_message}")
#             raise Exception(f"Search command failed: {error_message}")

#         # Parse the matched files from stdout
#         matched_files = [line.strip() for line in stdout_lines if line.strip()]

#         print(f"Matched files found: {matched_files}")
#         return matched_files

#     except Exception as e:
#         print(f"Error in search_wal_files_for_keyword: {str(e)}")
#         raise

# def search_wal_files_for_keyword(ssh, keyword, number_of_files):
#     """
#     Searches the most recently modified WAL files for a specific keyword on a remote server via SSH.
    
#     Args:
#         ssh (paramiko.SSHClient): The active SSH connection object.
#         keyword (str): The keyword to search for in WAL files.
#         number_of_files (int): Number of most recent WAL files to search in.

#     Returns:
#         list: A list of file paths that contain the keyword.
#     """
#     try:
#         if not keyword.strip():
#             raise ValueError("Keyword cannot be empty or whitespace.")
#         if number_of_files <= 0:
#             raise ValueError("Number of files must be greater than 0.")
        
#         escaped_keyword = shlex.quote(keyword.strip())
#         base_path = "/var/lib/edb/as16/data/pg_wal"

#         find_command = (
#             f'find {base_path} -type f -printf "%T@ %p\\n" | sort -nr | head -n {number_of_files} | '
#             f'cut -d\' \' -f2 | xargs -I{{}} bash -c \'strings "{{}}" | grep -q {escaped_keyword} && echo "{{}}"\''
#         )

#         print(f"Executing command on remote server: {find_command}")

#         # Execute the command on the remote server
#         stdin, stdout, stderr = ssh.exec_command(find_command)
#         stdout_lines = stdout.readlines()
#         stderr_lines = stderr.readlines()

#         # Check for errors
#         if stderr_lines:
#             error_message = ''.join(stderr_lines)
#             print(f"Error occurred during remote search: {error_message}")
#             raise Exception(f"Search command failed: {error_message}")

#         # Parse the matched files from stdout
#         matched_files = [line.strip() for line in stdout_lines if line.strip()]

#         print(f"Matched files found: {matched_files}")
#         return matched_files

#     except Exception as e:
#         print(f"Error in search_wal_files_for_keyword: {str(e)}")
#         raise

# def search_wal_files_for_keyword(shell, base_path, keyword, number_of_files):
#     """
#     Searches the most recently modified WAL files for a specific keyword via an interactive shell.

#     Args:
#         shell (paramiko.channel.Channel): The active shell channel for executing commands.
#         base_path (str): The base path of the WAL files directory.
#         keyword (str): The keyword to search for in the WAL files.
#         number_of_files (int): The number of most recently modified WAL files to search.

#     Returns:
#         list: A list of file paths containing the keyword.
#     """
#     try:
#         if not keyword.strip():
#             raise ValueError("Keyword cannot be empty or whitespace.")
#         if number_of_files <= 0:
#             raise ValueError("Number of files must be greater than 0.")

#         escaped_keyword = shlex.quote(keyword.strip())
#         command = (
#             f"find {base_path} -type f -printf '%T@ %p\\n' | sort -nr | "
#             f"head -n {number_of_files} | cut -d' ' -f2 | "
#             f"xargs -I{{}} bash -c 'strings \"{{}}\" | grep -q {escaped_keyword} && echo \"{{}}\"'\n"
#         )

#         print(f"Executing command: {command.strip()} (search_wal_files_for_keyword)")
#         shell.send(command)
#         time.sleep(1)  # Give the shell time to start executing the command

#         print("Capturing output... (search_wal_files_for_keyword)")
#         output = ""
#         while True:
#             output_chunk = shell.recv(1024).decode()
#             output += output_chunk
#             # Check if the command prompt reappeared, indicating command completion
#             if output.strip().endswith("$") or "Permission denied" in output:
#                 break

#         print("Processing output... (search_wal_files_for_keyword)")
#         # Extract matched files from the output
#         matched_files = [line.strip() for line in output.splitlines() if base_path in line]
        
#         print(f"Matched files: {matched_files}")
#         return matched_files

#     except Exception as e:
#         print(f"Error in search_wal_files_for_keyword: {str(e)}")
#         raise

<<<<<<< HEAD
def remove_color_codes(text):
    """
    Removes ANSI color codes from a string.
    
    Args:
        text (str): The input string potentially containing ANSI color codes.
        
    Returns:
        str: The string with color codes removed.
    """
    #return re.sub(r'(\x1b\[[0-9;]*[mK]|\x1b\[|\x1b)', '', text)
    return re.sub(r'(\x1b\[[0-9;]*[mK]|\x1b)', '', text)

def search_wal_files_and_content_for_keyword(shell, base_path, keyword, number_of_files, timeout=30):
=======
def search_wal_files_for_keyword(shell, base_path, keyword, number_of_files, timeout=30):
>>>>>>> abc1743438d1fe7ad3b01f888d4a1fe37db4edb6
    """
    Searches the most recently modified WAL files for a specific keyword via an interactive shell.

    Args:
        shell (paramiko.channel.Channel): The active shell channel for executing commands.
        base_path (str): The base path of the WAL files directory.
        keyword (str): The keyword to search for in the WAL files.
        number_of_files (int): The number of most recently modified WAL files to search.
        timeout (int): Maximum time (in seconds) to wait for command completion.

    Returns:
<<<<<<< HEAD
        list: A list of WAL file names containing the keyword.
=======
        list: A list of file paths containing the keyword.
>>>>>>> abc1743438d1fe7ad3b01f888d4a1fe37db4edb6
    """
    try:
        if not keyword.strip():
            raise ValueError("Keyword cannot be empty or whitespace.")
        if number_of_files <= 0:
            raise ValueError("Number of files must be greater than 0.")

        escaped_keyword = shlex.quote(keyword.strip())
        command = (
            f"find {base_path} -type f -printf '%T@ %p\\n' | sort -nr | "
            f"head -n {number_of_files} | cut -d' ' -f2 | "
            f"xargs -I{{}} bash -c 'strings \"{{}}\" | grep -q {escaped_keyword} && echo \"{{}}\"'\n"
        )

        print(f"Executing command: {command.strip()} (search_wal_files_for_keyword)")
        shell.send(command)

        start_time = time.time()
        output = ""

        print("Capturing output... (search_wal_files_for_keyword)")
        while True:
            # Check for timeout
            if time.time() - start_time > timeout:
                raise TimeoutError("Command execution timed out.")

            if shell.recv_ready():
                output_chunk = shell.recv(1024).decode()
                output += output_chunk

                # If the output contains the command prompt or output ends
                if output.strip().endswith("$") or base_path in output:
                    break

            time.sleep(0.5)  # Reduce CPU usage in the loop

        print("Processing output... (search_wal_files_for_keyword)")
<<<<<<< HEAD
        # Extract only the file names from the output
        matched_files = [os.path.basename(line.strip()) for line in output.splitlines() if base_path in line]

        print(f"Matched file names: {matched_files}")

        result = []

        # For each matched file, extract the content containing the keyword
        for wal_file in matched_files[1:]:
            file_content_command = f"strings {base_path}/{wal_file} | grep -i {escaped_keyword}\n"
            print(f"Executing command to fetch content: {file_content_command.strip()}")
            shell.send(file_content_command)

            file_output = ""
            while True:
                if time.time() - start_time > timeout:
                    raise TimeoutError("Command execution timed out.")

                if shell.recv_ready():
                    output_chunk = shell.recv(1024).decode()
                    print(output_chunk)
                    file_output += output_chunk + "\n"  # Add a newline after each chunk

                # If the output contains the command prompt or output ends
                if not shell.recv_ready() and file_output.strip():
                    break

                time.sleep(0.5)  # Reduce CPU usage in the loop

            # Remove color codes from the file output
            file_output_cleaned = remove_color_codes(file_output)

            # Store the WAL file name and its matching lines
            matched_lines = file_output_cleaned.splitlines()
            print
            result.append([wal_file, matched_lines])
        return result
=======
        # Extract matched files from the output
        matched_files = [line.strip() for line in output.splitlines() if base_path in line]

        print(f"Matched files: {matched_files}")
        return matched_files
>>>>>>> abc1743438d1fe7ad3b01f888d4a1fe37db4edb6

    except Exception as e:
        print(f"Error in search_wal_files_for_keyword: {str(e)}")
        raise


<<<<<<< HEAD

# def run_full_process(host, ssh_user, ssh_password, keyword, number_of_files):
#     """
#     Orchestrates the full process of fetching WAL files and searching for a keyword.
#     """
#     try:
#         print(f"Executing run_full_process in wal_handler.py with host={host}, "
#               f"ssh_user={ssh_user}, keyword={keyword}")

#         ssh = connect_via_ssh(host, ssh_user, ssh_password)
#         print("SSH connection established.")
#         shell = ssh.invoke_shell()

#         switch_to_root(shell, ssh_password)
#         print("Switched to root user.")

#         # Search for the keyword
#         matched_files = search_wal_files_for_keyword(shell, keyword, number_of_files)
        
#         ssh.close()
#         print("SSH connection closed.")

#         if matched_files:
#             print(f"Files matched: {matched_files}")
#             return {
#                 "status": "success",
#                 "matched_files": matched_files
#             }
#         else:
#             print("No matches found.")
#             return {
#                 "status": "success",
#                 "message": "No matches found.",
#                 "matched_files": []
#             }

#     except Exception as e:
#         print(f"Error in run_full_process: {str(e)}")
#         return {"status": "error", "message": str(e)}

=======
# def run_full_process(host, ssh_user, ssh_password, keyword, number_of_files):
#     """
#     Orchestrates the full process of fetching WAL files and searching for a keyword.
#     """
#     try:
#         print(f"Executing run_full_process in wal_handler.py with host={host}, "
#               f"ssh_user={ssh_user}, keyword={keyword}")

#         ssh = connect_via_ssh(host, ssh_user, ssh_password)
#         print("SSH connection established.")
#         shell = ssh.invoke_shell()

#         switch_to_root(shell, ssh_password)
#         print("Switched to root user.")

#         # Search for the keyword
#         matched_files = search_wal_files_for_keyword(shell, keyword, number_of_files)
        
#         ssh.close()
#         print("SSH connection closed.")

#         if matched_files:
#             print(f"Files matched: {matched_files}")
#             return {
#                 "status": "success",
#                 "matched_files": matched_files
#             }
#         else:
#             print("No matches found.")
#             return {
#                 "status": "success",
#                 "message": "No matches found.",
#                 "matched_files": []
#             }

#     except Exception as e:
#         print(f"Error in run_full_process: {str(e)}")
#         return {"status": "error", "message": str(e)}

>>>>>>> abc1743438d1fe7ad3b01f888d4a1fe37db4edb6
def run_full_process(host, ssh_user, ssh_password, keyword, number_of_files):
    """
    Orchestrates the full process of fetching WAL files and searching for a keyword.
    """
    try:
        print(f"Executing run_full_process with host={host}, user={ssh_user}, keyword={keyword}")
<<<<<<< HEAD

        ssh = connect_via_ssh(host, ssh_user, ssh_password)
        print("SSH connection established.")
        shell = ssh.invoke_shell()

        switch_to_root(shell, ssh_password)
        print("Switched to root user.")

        # Specify the WAL directory path
        base_path = "/var/lib/edb/as15/data/pg_wal"


        # Search for the keyword
        matched_files = search_wal_files_and_content_for_keyword(shell, base_path, keyword, number_of_files)
=======

        ssh = connect_via_ssh(host, ssh_user, ssh_password)
        print("SSH connection established.")
        shell = ssh.invoke_shell()

        switch_to_root(shell, ssh_password)
        print("Switched to root user.")

        # Specify the WAL directory path
        base_path = "/var/lib/edb/as15/data/pg_wal"

        # Search for the keyword
        matched_files = search_wal_files_for_keyword(shell, base_path, keyword, number_of_files)
>>>>>>> abc1743438d1fe7ad3b01f888d4a1fe37db4edb6

        shell.close()
        ssh.close()
        print("SSH connection closed.")

        if matched_files:
            return {"status": "success", "matched_files": matched_files}
        else:
            return {"status": "success", "message": "No matches found.", "matched_files": []}

    except Exception as e:
        print(f"Error in run_full_process: {str(e)}")
        return {"status": "error", "message": str(e)}
