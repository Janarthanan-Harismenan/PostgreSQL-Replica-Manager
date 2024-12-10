import paramiko
import time
import re
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def connect_via_ssh(host, ssh_user, ssh_password):
    """
    Establishes an SSH connection to the remote server.
    """
    try:
        print("Establishing SSH connection...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=ssh_user, password=ssh_password)
        print("SSH connection established.")
        return ssh
    except Exception as e:
        print(f"Error connecting to SSH: {str(e)}")
        raise

def switch_to_root(shell, ssh_password):
    """
    Switches to the root user via sudo in the SSH session.
    """
    print("Running sudo to switch to root user...")
    shell.send("sudo -i\n")
    time.sleep(1)  # Wait for sudo to prompt for password
    shell.send(ssh_password + "\n")  # Enter sudo password
    time.sleep(1)  # Wait for the command to execute

def switch_to_enterprisedb(shell):
    """
    Switches to the 'enterprisedb' user in the SSH session.
    """
    print("Switching to 'enterprisedb' user...")
    shell.send("su - enterprisedb\n")
    time.sleep(1)  # Wait for the 'enterprisedb' user prompt

def run_pg_catcheck(shell, pg_host, port, user, database, pg_password):
    """
    Runs the `pg_catcheck` command and captures its output.
    """
    command = f"/usr/edb/as15/bin/pg_catcheck -h {pg_host} -p {port} -U {user} {database} --verbose | sed '1,/verbose/d'\n"
    print(f"Executing command: {command.strip()}")
    shell.send(command)
    time.sleep(1)  # Wait for the command prompt

    print("Sending pg_password...")
    shell.send(pg_password + "\n")
    time.sleep(5)  # Allow time for the password to be processed and output to be generated

    print("Capturing output...")
    output = ""
    while True:
        output_chunk = shell.recv(1024).decode()
        output += output_chunk
        if "done" in output.lower() or "error" in output.lower():  # Check if the command execution finished or if an error occurs
            break

    # Remove everything before the first 'verbose'
    output = re.split(r'verbose', output, 1)[-1]
    output = "verbose" + output  # Re-add 'verbose' to the start of the string

    return output

def extract_results(output):
    """
    Extracts inconsistencies, warnings, and errors from the pg_catcheck output.
    """
    inconsistencies = re.findall(r'inconsistencies: (\d+)', output)
    warnings = re.findall(r'warnings: (\d+)', output)
    errors = re.findall(r'errors: (\d+)', output)

    return {
        "inconsistencies": inconsistencies[0] if inconsistencies else 0,
        "warnings": warnings[0] if warnings else 0,
        "errors": errors[0] if errors else 0
    }

def run_pg_catcheck_via_ssh(host, ssh_user, ssh_password, pg_host, port, user, database, pg_password):
    """
    Orchestrates the SSH connection, user switching, and `pg_catcheck` execution.
    """
    try:
        ssh = connect_via_ssh(host, ssh_user, ssh_password)
        shell = ssh.invoke_shell()

        switch_to_root(shell, ssh_password)
        switch_to_enterprisedb(shell)
        output = run_pg_catcheck(shell, pg_host, port, user, database, pg_password)

        print("Command execution completed. Closing SSH connection...")
        ssh.close()

        results = extract_results(output)
        return {
            "status": "success",
            "output": output,
            **results
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {"status": "error", "message": str(e)}


def convert_log_to_pdf(log_output, filename="pg_catcheck_output.pdf"):
    """
    Converts the log output to a PDF file.
    """
    print("Converting log to PDF...")
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    # Add the log content to the PDF
    text_object = c.beginText(40, height - 40)
    text_object.setFont("Helvetica", 10)
    text_object.setTextOrigin(40, height - 40)

    print("Adding content to PDF...")
    for line in log_output.splitlines():
        text_object.textLine(line)

    c.drawText(text_object)
    c.showPage()
    c.save()

    print(f"PDF saved as {filename}")
    return filename