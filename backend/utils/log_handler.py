import os
import shlex
import subprocess
from utils.db_utils import flush_shell_output, switch_to_enterprisedb, switch_to_root, connect_via_ssh
import time
import re
from config import LOG_PATH_CONFIG

def get_last_modified_log_files(shell, base_path, number_of_files=10, timeout=30):
    """
    Retrieves the last N modified log files from a specified directory via an interactive shell.
 
    Args:
        shell (paramiko.channel.Channel): The active shell channel for executing commands.
        base_path (str): The base path of the log files directory.
        number_of_files (int): The number of most recently modified log files to retrieve.
        timeout (int): Maximum time (in seconds) to wait for command completion.
 
    Returns:
        list: A list of the last N modified log file names.
    """
    try:
        if number_of_files <= 0:
            raise ValueError("Number of files must be greater than 0.")
 
        command = (
            f"find {base_path} -type f -printf '%T@ %p\\n' | sort -nr | "
            f"head -n {number_of_files} | cut -d' ' -f2"
        )
 
        print(f"Executing command: {command.strip()} (get_last_modified_log_files)")
        shell.send(command + "\n")
 
        start_time = time.time()
        output = ""
 
        print("Capturing output... (get_last_modified_log_files)")
        while True:
            # Check for timeout
            if time.time() - start_time > timeout:
                raise TimeoutError("Command execution timed out.")
 
            if shell.recv_ready():
                output_chunk = shell.recv(1024).decode()
                output += output_chunk
 
                # If the output contains the command prompt or output ends
                if output.strip().endswith("$") :
                    break
 
            time.sleep(0.5)  # Reduce CPU usage in the loop
 
        print("Processing output... (get_last_modified_log_files)")
        # Extract only the file names from the output
        matched_files = [os.path.basename(line.strip()) for line in output.splitlines() if base_path in line]
 
        print(f"Matched log files: {matched_files[1:]}")
 
        return matched_files[1:]
 
    except Exception as e:
        print(f"Error in get_last_modified_log_files: {str(e)}")
        raise e
 
def fetch_last_10_logs(host, ssh_user, ssh_password, number_of_files=10):
    """
    Orchestrates the process of fetching the last N modified log files from a remote server.
 
    Args:
        host (str): The remote host's address.
        ssh_user (str): The SSH username.
        ssh_password (str): The SSH password.
        number_of_files (int): The number of log files to fetch (default is 10).
 
    Returns:
        dict: A dictionary with the status and the list of log files.
    """
    try:
        print(f"Executing fetch_last_10_logs with host={host}, user={ssh_user}")
        ssh = connect_via_ssh(host, ssh_user, ssh_password)
        print("SSH connection established.")
        shell = ssh.invoke_shell()

        switch_to_root(shell, ssh_password)
        print("Switched to root user.")
        switch_to_enterprisedb(shell)
        print("Switched to 'enterprisedb' user.")
        
        base_path = LOG_PATH_CONFIG.get("log_base_path")
        
        # Specify the log directory path
        # base_path = "/u01/edb/as15/data/log"  # Adjust to your log directory

        # Fetch the last N modified log files
        log_files = get_last_modified_log_files(shell, base_path, number_of_files=number_of_files)

        shell.close()
        ssh.close()
        print("SSH connection closed.")

        if log_files:
            return {"status": "success", "log_files": log_files}
        else:
            return {"status": "success", "message": "No log files found.", "log_files": []}

    except Exception as e:
        print(f"Error in fetch_last_10_logs: {str(e)}")
        return {"status": "error", "message": str(e)}
 
def search_log_file_for_keyword(ssh_host, ssh_user, ssh_password, log_file_path, keyword, context_lines=5, timeout=30):
    """
    Searches a log file for a given keyword and retrieves matched lines with context.
   
    Args:
        ssh_host (str): The SSH host address.
        ssh_user (str): The SSH username.
        ssh_password (str): The SSH password.
        log_file_path (str): The full path to the log file.
        keyword (str): The keyword to search for in the log file.
        context_lines (int): Number of lines before and after each match to retrieve.
        timeout (int): Maximum time (in seconds) to wait for command completion.
   
    Returns:
        list: A 2D list where each element contains:
              [matched_line, before_context, after_context]
    """
    try:
        if not keyword.strip():
            raise ValueError("Keyword cannot be empty or whitespace.")
 
        ssh = connect_via_ssh(ssh_host, ssh_user, ssh_password)
        print("SSH connection established.")
        shell = ssh.invoke_shell()
 
        switch_to_root(shell, ssh_password)
        print("Switched to root user.")
        switch_to_enterprisedb(shell)
        print("Switched to 'enterprisedb' user.")
 
        escaped_keyword = shlex.quote(keyword.strip())
        grep_command = f"grep -n '{escaped_keyword}' {log_file_path}\n"
 
        print(f"Executing command: {grep_command} (search_log_file_for_keyword_with_context)")
        flush_shell_output(shell)
        shell.send(grep_command)
 
        start_time = time.time()
        output = ""
 
        print("Capturing output... (search_log_file_for_keyword_with_context)")
        while True:
            if time.time() - start_time > timeout:
                raise TimeoutError("Command execution timed out.")
 
            if shell.recv_ready():
                output_chunk = shell.recv(1024).decode()
                output += output_chunk
 
                if output.strip().endswith("$") or log_file_path in output:
                    break
 
            time.sleep(0.5)
 
        print("Processing matched lines... (search_log_file_for_keyword_with_context)")
        output_cleaned = re.sub(r'(\x1b\[[0-9;]*[mK]|\x1b)', '', output)  # Remove ANSI escape codes
        matched_lines = []
        for line in output_cleaned.splitlines():
            if ":" in line:
                try:
                    line_num, content = line.split(":", 1)
                    matched_lines.append((int(line_num), content.strip()))
                except ValueError:
                    continue
 
        if not matched_lines:
            print("No matches found.")
            return []
 
        # Fetch context for each matched line
        results = []
        for line_num, content in matched_lines:
            start_line = max(1, line_num - context_lines)
            end_line = line_num + context_lines
            context_command = f"sed -n '{start_line},{end_line}p' {log_file_path}\n"
           
            print(f"Fetching context for line {line_num} using command: {context_command}")
            flush_shell_output(shell)
            shell.send(context_command)
 
            context_output = ""
            while True:
                if time.time() - start_time > timeout:
                    raise TimeoutError("Context command execution timed out.")
 
                if shell.recv_ready():
                    context_chunk = shell.recv(1024).decode()
                    context_output += context_chunk
 
                    if context_output.strip().endswith("$") or log_file_path in context_output:
                        break
 
                time.sleep(0.5)
 
            # Clean up and split context lines
            context_cleaned = re.sub(r'(\x1b\[[0-9;]*[mK]|\x1b)', '', context_output)
            context_lines_split = context_cleaned.strip().splitlines()
            print(context_lines_split)
            # Store the matched line with its context
            before_context = context_lines_split[1:context_lines+1]
            after_context = context_lines_split[context_lines + 2:] if len(context_lines_split) > context_lines else []
            results.append([content, before_context, after_context])
 
        shell.close()
        ssh.close()
 
        print("Results with context retrieved successfully.")
        return results
 
    except Exception as e:
        print(f"Error in search_log_file_for_keyword_with_context: {str(e)}")
        raise e