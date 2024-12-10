import os
import subprocess
from utils.pg_catcheck import connect_via_ssh

def get_wal_files_via_ssh(ssh, wal_dir, num_files):
    """
    Fetches the specified number of WAL files from the PostgreSQL server.
    """
    print("Fetching WAL files...")
    sftp = ssh.open_sftp()

    # List and sort WAL files in the directory
    try:
        wal_files = sorted(sftp.listdir(wal_dir))[-num_files:]
    except Exception as e:
        raise RuntimeError(f"Error listing WAL directory: {str(e)}")

    local_wal_dir = "wal_files"
    os.makedirs(local_wal_dir, exist_ok=True)  # Create a local directory to save WAL files

    downloaded_files = []
    for wal_file in wal_files:
        remote_path = os.path.join(wal_dir, wal_file)
        local_path = os.path.join(local_wal_dir, wal_file)

        try:
            print(f"Downloading {wal_file}...")
            sftp.get(remote_path, local_path)
            downloaded_files.append(local_path)
        except Exception as e:
            print(f"Error downloading {wal_file}: {str(e)}")

    sftp.close()
    return downloaded_files


def search_wal_files_for_keyword(wal_files, keyword):
    """
    Searches for a keyword in the provided WAL files using `pg_waldump`.
    """
    print(f"Searching for keyword '{keyword}' in WAL files...")
    matched_files = []

    for wal_file in wal_files:
        try:
            # Execute pg_waldump to parse the WAL file
            command = ["pg_waldump", wal_file]
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            if result.returncode != 0:
                print(f"Error reading {wal_file}: {result.stderr}")
                continue

            if keyword in result.stdout:
                matched_files.append(wal_file)
                print(f"Keyword found in {wal_file}")

        except Exception as e:
            print(f"Error processing {wal_file}: {str(e)}")

    return matched_files


def run_full_process(host, ssh_user, ssh_password, wal_dir, num_files, keyword):
    """
    Orchestrates the full process of fetching WAL files and searching for a keyword.
    """
    try:
        ssh = connect_via_ssh(host, ssh_user, ssh_password)
        print("Connected to server via SSH.")

        # Fetch the WAL files
        wal_files = get_wal_files_via_ssh(ssh, wal_dir, num_files)
        print(f"Downloaded WAL files: {wal_files}")

        # Search for the keyword
        matched_files = search_wal_files_for_keyword(wal_files, keyword)

        print("Closing SSH connection...")
        ssh.close()

        if matched_files:
            return {
                "status": "success",
                "matched_files": matched_files
            }
        else:
            return {
                "status": "success",
                "message": "No matches found.",
                "matched_files": []
            }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {"status": "error", "message": str(e)}