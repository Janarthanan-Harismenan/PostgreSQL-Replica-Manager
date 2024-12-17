import os
import shlex
import time
import re
from utils.db_utils import switch_to_root, connect_via_ssh

def search_wal_files_and_content_for_keyword(shell, base_path, keyword, number_of_files, timeout=30):
    """
    Searches the most recently modified WAL files for a specific keyword via an interactive shell.
 
    Args:
        shell (paramiko.channel.Channel): The active shell channel for executing commands.
        base_path (str): The base path of the WAL files directory.
        keyword (str): The keyword to search for in the WAL files.
        number_of_files (int): The number of most recently modified WAL files to search.
        timeout (int): Maximum time (in seconds) to wait for command completion.
 
    Returns:
        list: A list of WAL file names containing the keyword.
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
            file_output_cleaned = re.sub(r'(\x1b\[[0-9;]*[mK]|\x1b)', '', file_output)
 
            # Store the WAL file name and its matching lines
            matched_lines = file_output_cleaned.splitlines()
            print
            result.append([wal_file, matched_lines])
        return result
 
    except Exception as e:
        print(f"Error in search_wal_files_for_keyword: {str(e)}")
        raise
 
def run_full_process(host, ssh_user, ssh_password, keyword, number_of_files):
    """
    Orchestrates the full process of fetching WAL files and searching for a keyword.
    """
    try:
        print(f"Executing run_full_process with host={host}, user={ssh_user}, keyword={keyword}")
 
        ssh = connect_via_ssh(host, ssh_user, ssh_password)
        print("SSH connection established.")
        shell = ssh.invoke_shell()
 
        switch_to_root(shell, ssh_password)
        print("Switched to root user.")
 
        # Specify the WAL directory path
        base_path = "/var/lib/edb/as15/data/pg_wal"
 
 
        # Search for the keyword
        matched_files = search_wal_files_and_content_for_keyword(shell, base_path, keyword, number_of_files)
 
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