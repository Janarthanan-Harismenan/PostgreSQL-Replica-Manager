import os
import shlex
import subprocess
from utils.db_utils import switch_to_root, connect_via_ssh, switch_to_enterprisedb
import time
import re
import json
from config import PATH_CONFIG

def remove_color_codes(text):
    """
    Removes ANSI color codes from a string.

    Args:
        text (str): The input string potentially containing ANSI color codes.

    Returns:
        str: The string with color codes removed.
    """
    return re.sub(r'(\x1b\[[0-9;]*[mK]|\x1b)', '', text)

def extract_wal_file_details(matched_files, wal_file_name):
    """
    Extracts and filters details for a specific WAL file from the matched_files result.

    Args:
        matched_files (list): The list of matched WAL files with their details.
        wal_file_name (str): The WAL file name to extract details for.

    Returns:
        list: Lines of relevant details for the specified WAL file.
    """
    for file_entry in matched_files:
        if file_entry[0].endswith(wal_file_name):
            # Return the detailed output for the matched WAL file
            return [line.strip() for line in file_entry[1] if line.strip()]
    return []

def filter_output_between_patterns(output_lines, start_pattern, end_pattern):
    """
    Filters lines from the output between two specific patterns, handling multiple occurrences.

    Args:
        output_lines (list): List of output lines to filter.
        start_pattern (str): The start pattern to begin filtering.
        end_pattern (str): The end pattern to stop filtering.

    Returns:
        list: The filtered lines between the start and end pattern, excluding the end pattern itself.
    """
    filtered_lines = []
    capture = False
    current_block = []

    for line in output_lines:
        if start_pattern in line:
            # When the start pattern is found, start capturing the lines
            if current_block:
                filtered_lines.append(current_block)  # Append previous captured block if exists
            current_block = []  # Start a new block
            capture = True
            continue  # Skip the start pattern line
        if end_pattern in line:
            # When the end pattern is found, stop capturing
            if capture:
                # Do not add the end pattern line itself
                filtered_lines.append(current_block)  # Add the current block to the result
                current_block = []  # Reset the current block
            capture = False
            continue  # Skip the end pattern line
        if capture:
            current_block.append(line.strip())  # Capture the lines in between start and end pattern

    if current_block:  # In case there's an unfinished block at the end
        filtered_lines.append(current_block)

    return filtered_lines

import re

# def extract_after_drop_dir(lines):
#     """
#     Extracts the content that appears after "DROP dir" in the given lines.

#     Args:
#         lines (list): List of lines to search for "DROP dir".

#     Returns:
#         list: Extracted content appearing after "DROP dir".
#     """
#     extracted_items = []
#     for line in lines:
#         match = re.search(r"DROP dir\s+(.*?)\s", line)
#         if match:
#             extracted_items.append(match.group(1))
#     return extracted_items

def extract_after_drop_dir(lines):
    """
    Extracts the content that appears after "DROP dir" in the given lines.

    Args:
        lines (list): List of lines to search for "DROP dir".

    Returns:
        list: Extracted content appearing after "DROP dir".
    """
    extracted_items = []
    for line in lines:
        match = re.search(r"DROP dir\s+(\S+)", line)
        if match:
            extracted_items.append(match.group(1))
    return extracted_items

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
        print("escaped_keyword:", escaped_keyword)

        command = (
            f"find {base_path} -type f ! -path \"*/archive_status/*\" -printf \"%T@ %p\\n\" | sort -nr | "
            f"head -n {number_of_files}\n"
        )

        print(f"Executing command: {command.strip()} (search_wal_files_for_keyword)")
        shell.send(command)

        start_time = time.time()
        output = ""

        print("Capturing output... (search_wal_files_for_keyword)")
        while True:
            if time.time() - start_time > timeout:
                raise TimeoutError("Command execution timed out.")

            if shell.recv_ready():
                output_chunk = shell.recv(1024).decode()
                output += output_chunk

                # Break if the command prompt appears or output ends
                if output.strip().endswith("$") or base_path in output:
                    break

            time.sleep(0.5)  # Reduce CPU usage in the loop

        print("Processing output... (search_wal_files_for_keyword)")
        # Extract only the file paths from the output
        matched_files = [
            line.split(maxsplit=1)[-1].strip()  # Split by space and take the file path
            for line in output.splitlines()
            if base_path in line and len(line.split(maxsplit=1)) > 1  # Ensure there's a timestamp and path
        ]

        print(f"Matched file paths: {matched_files}")

        result = []

        # Use pg_waldump to inspect each WAL file
        for wal_file in matched_files:
            file_content_command = (
                f"/usr/edb/as15/bin/pg_waldump {wal_file} | grep -i {escaped_keyword}\n"
            )
            print(f"Executing pg_waldump command: {file_content_command.strip()}")
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

            # Split the cleaned output into lines
            file_output_lines = file_output_cleaned.splitlines()

            # Filter lines between "grep -i drop" and "-bash-4.2$"
            filtered_lines = filter_output_between_patterns(file_output_lines, "grep -i drop", "-bash-4.2$")

            # Extract content after "DROP dir"
            extracted_content = extract_after_drop_dir(file_output_lines)

            # Store the WAL file name, its matching lines, and extracted content
            result.append({
                "wal_file": os.path.basename(wal_file),
                "filtered_lines": filtered_lines,
                "extracted_content": extracted_content
            })

        return result

    except Exception as e:
        print(f"Error in search_wal_files_for_keyword: {str(e)}")
        raise e

def read_database_details():
    """
    Reads the database_details.json file and returns its content.
    """
    try:
        with open('database_details.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading database_details.json: {str(e)}")
        return {}

def match_database_with_dir(extracted_content, database_details):
    """
    Matches extracted directory content with the ones in database_details.

    Args:
        extracted_content (list): List of directories extracted from WAL files.
        database_details (list): List containing database details as dictionaries.

    Returns:
        dict: Matched database name and directory, or a message and unmatched directories if no match is found.
    """
    print("extracted_content :", extracted_content)
    print("database_details :", database_details)
    
    for db in database_details:  # Assume database_details is a list
        if db["dir"] in extracted_content:
            return {
                "database_name": db["name"],
                "database_dir": db["dir"]
            }
    
    # If no match is found, include the unmatched directories in the response
    return {
        "message": "No database with that name found.",
        "unmatched_directories": extracted_content
    }

def run_full_process(host, ssh_user, ssh_password, keyword, number_of_files, selected_path, wal_file_name=None):
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

        switch_to_enterprisedb(shell)

        # Specify the WAL directory path
        # base_path = "/u01/edb/as15/data/pg_wal"
        # base_path_archive = "/u01/edb/as15/archivedir"
        
        base_path = selected_path
        
        # Search for the keyword
        matched_files = search_wal_files_and_content_for_keyword(shell, base_path, keyword, number_of_files)

        # Read the database details from the JSON file
        database_details = read_database_details()

        # Integrate database match information directly into matched_files
        for file in matched_files:
            extracted_content = file.get("extracted_content", [])
            db_match = match_database_with_dir(extracted_content, database_details)
            file["db_info"] = db_match  # Add the database match information directly to the file

        shell.close()
        ssh.close()
        print("SSH connection closed.")

        if wal_file_name:
            # Extract details for the specific WAL file
            wal_file_details = extract_wal_file_details(matched_files, wal_file_name)
            return {"status": "success", "wal_file_details": wal_file_details, "matched_files": matched_files}

        if matched_files:
            return {"status": "success", "matched_files": matched_files[1:]}
        else:
            return {"status": "success", "message": "No matches found.", "matched_files": []}

    except Exception as e:
        print(f"Error in run_full_process: {str(e)}")
        return {"status": "error", "message": str(e)}