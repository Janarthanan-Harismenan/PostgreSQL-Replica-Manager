import os
import shlex
import subprocess
import time
import re
import json
from utils.db_utils import switch_to_root, connect_via_ssh, switch_to_enterprisedb, flush_shell_output
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
        if file_entry["wal_file"] == wal_file_name:
            return file_entry["content"]
    return []

def filter_output_between_patterns(output_text, start_pattern, end_pattern):
    """
    Filters lines from the output text between two specific patterns, handling multiple occurrences.

    Args:
        output_text (str): The text to filter.
        start_pattern (str): The start pattern to begin filtering.
        end_pattern (str): The end pattern to stop filtering.

    Returns:
        str: The filtered text between the start and end patterns, excluding the patterns themselves.
    """
    filtered_blocks = []
    capture = False
    current_block = []

    output_lines = output_text.splitlines()  # Split the input text into lines

    for line in output_lines:
        if start_pattern in line:
            if current_block:
                filtered_blocks.append("\n".join(current_block))  # Join the captured lines into a block
            current_block = []
            capture = True
            continue
        if end_pattern in line:
            if capture:
                filtered_blocks.append("\n".join(current_block))  # Append the current block to results
                current_block = []
            capture = False
            continue
        if capture:
            current_block.append(line.strip())

    if current_block:
        filtered_blocks.append("\n".join(current_block))  # Append the final block, if any

    return "\n\n".join(filtered_blocks)  # Join all blocks into a single string, separated by newlines

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

# def search_wal_files_and_content_for_keyword(shell, base_path, keyword, number_of_files, timeout=30):
#     """
#     Searches the most recently modified WAL files for a specific keyword via an interactive shell.

#     Args:
#         shell (paramiko.channel.Channel): The active shell channel for executing commands.
#         base_path (str): The base path of the WAL files directory.
#         keyword (str): The keyword to search for in the WAL files.
#         number_of_files (int): The number of most recently modified WAL files to search.
#         timeout (int): Maximum time (in seconds) to wait for command completion.

#     Returns:
#         list: A list of dictionaries containing WAL file names and their matched content.
#     """
#     try:
#         if not keyword.strip():
#             raise ValueError("Keyword cannot be empty or whitespace.")
#         if number_of_files <= 0:
#             raise ValueError("Number of files must be greater than 0.")

#         escaped_keyword = shlex.quote(keyword.strip())
#         command = (
#             f"find {base_path} -type f ! -path \"*/archive_status/*\" -printf \"%T@ %p\\n\" | sort -nr | "
#             f"head -n {number_of_files}\n"
#         )
#         shell.send(command)

#         start_time = time.time()
#         output = ""

#         while True:
#             if time.time() - start_time > timeout:
#                 raise TimeoutError("Command execution timed out.")

#             if shell.recv_ready():
#                 output_chunk = shell.recv(1024).decode()
#                 output += output_chunk

#                 if output.strip().endswith("$"):
#                     break

#             time.sleep(0.5)

#         matched_files = [
#             line.split(maxsplit=1)[-1].strip()
#             for line in output.splitlines()
#             if base_path in line and len(line.split(maxsplit=1)) > 1
#         ]
        
#         matched_files = matched_files[1:]
        
#         # print("---------------------------------------matched_files :",matched_files)

#         result = []
        
#         # print("helooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo")
#         flush_shell_output(shell)

#         for wal_file in matched_files:
#             file_content_command = (
#                 f"/usr/edb/as15/bin/pg_waldump {wal_file} | grep -i {escaped_keyword}\n"
#             )
#             print(file_content_command)
#             shell.send(file_content_command)
            
#             file_output = ""
#             while True:
                
#                 if time.time() - start_time > timeout:
#                     raise TimeoutError("Command execution timed out.")

#                 if shell.recv_ready():
#                     output_chunk = shell.recv(1024).decode()
#                     file_output += output_chunk + "\n"

#                 if not shell.recv_ready() and file_output.strip():
#                     break

#                 time.sleep(0.5)
            
#             file_output_cleaned = remove_color_codes(file_output)
            
#             file_output = filter_output_between_patterns(file_output_cleaned, f"grep -i {escaped_keyword}", "-bash-4.2$")
            
#             print("Type ------------------------------------------------------------------",type(file_output))

#             result.append({
#                 "wal_file": os.path.basename(wal_file),
#                 "content": file_output.strip()
#             })

#         return result

#     except Exception as e:
#         raise e

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
        list: A list of dictionaries containing WAL file names and their matched content as a list of lines.
    """
    try:
        if not keyword.strip():
            raise ValueError("Keyword cannot be empty or whitespace.")
        if number_of_files <= 0:
            raise ValueError("Number of files must be greater than 0.")

        escaped_keyword = shlex.quote(keyword.strip())
        command = (
            f"find {base_path} -type f ! -path \"*/archive_status/*\" -printf \"%T@ %p\\n\" | sort -nr | "
            f"head -n {number_of_files}\n"
        )
        shell.send(command)

        start_time = time.time()
        output = ""

        while True:
            if time.time() - start_time > timeout:
                raise TimeoutError("Command execution timed out.")

            if shell.recv_ready():
                output_chunk = shell.recv(1024).decode()
                output += output_chunk

                if output.strip().endswith("$"):
                    break

            time.sleep(0.5)

        matched_files = [
            line.split(maxsplit=1)[-1].strip()
            for line in output.splitlines()
            if base_path in line and len(line.split(maxsplit=1)) > 1
        ]
        
        matched_files = matched_files[1:]
        
        flush_shell_output(shell)

        result = []

        for wal_file in matched_files:
            file_content_command = (
                f"/usr/edb/as15/bin/pg_waldump {wal_file} | grep -i {escaped_keyword}\n"
            )
            print(file_content_command)
            shell.send(file_content_command)
            
            file_output = ""
            while True:
                if time.time() - start_time > timeout:
                    raise TimeoutError("Command execution timed out.")

                if shell.recv_ready():
                    output_chunk = shell.recv(1024).decode()
                    file_output += output_chunk + "\n"

                if not shell.recv_ready() and file_output.strip():
                    break

                time.sleep(0.5)
            
            file_output_cleaned = remove_color_codes(file_output)
            file_output = filter_output_between_patterns(file_output_cleaned, f"grep -i {escaped_keyword}", "-bash-4.2$")
            
            # Split the file output into a list of lines
            file_output_list = [line.strip() for line in file_output.splitlines() if line.strip()]

            result.append({
                "wal_file": os.path.basename(wal_file),
                "content": file_output_list  # Returning as a list
            })

        return result

    except Exception as e:
        raise e

def read_database_details():
    """
    Reads the database_details.json file and returns its content.
    """
    try:
        with open('database_details.json', 'r') as f:
            return json.load(f)
    except Exception as e:
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
    for db in database_details:
        if db["dir"] in extracted_content:
            return {
                "database_name": db["name"],
                "database_dir": db["dir"]
            }
    return {
        "message": "No database with that name found.",
        "unmatched_directories": extracted_content
    }

def run_full_process(host, ssh_user, ssh_password, keyword, number_of_files, selected_path, wal_file_name=None):
    """
    Orchestrates the full process of fetching WAL files and searching for a keyword.
    """
    try:
        ssh = connect_via_ssh(host, ssh_user, ssh_password)
        shell = ssh.invoke_shell()

        switch_to_root(shell, ssh_password)
        
        switch_to_enterprisedb(shell)

        base_path = selected_path

        matched_files = search_wal_files_and_content_for_keyword(shell, base_path, keyword, number_of_files)

        database_details = read_database_details()

        for file in matched_files:
            # extracted_content = extract_after_drop_dir(file["content"].splitlines())
            extracted_content = extract_after_drop_dir(file["content"])
            db_match = match_database_with_dir(extracted_content, database_details)
            file["db_info"] = db_match

        shell.close()
        ssh.close()
        
        # matched_files = matched_files[1:]

        if wal_file_name:
            wal_file_details = extract_wal_file_details(matched_files, wal_file_name)
            return {"status": "success", "wal_file_details": wal_file_details, "matched_files": matched_files}

        return {"status": "success", "matched_files": matched_files}

    except Exception as e:
        return {"status": "error", "message": str(e)}
