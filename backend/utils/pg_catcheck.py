import time
import re
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from utils.db_utils import switch_to_server
 
def run_pg_catcheck_via_ssh(shell, pg_host, port, user, database, pg_password):
    """
    Orchestrates the SSH connection, user switching, and `pg_catcheck` execution.
    """
    try:
        print("Starting pg_catcheck process... (pg_catcheck.py)")
        # ssh = connect_via_ssh(host, ssh_user, ssh_password)
        # shell = ssh.invoke_shell()
 
        # switch_to_root(shell, ssh_password)
        # switch_to_enterprisedb(shell)
        switch_to_server(shell,pg_host)
        output = run_pg_catcheck(shell, pg_host, port, user, database, pg_password)
 
        print("Command execution completed. Closing SSH connection... (pg_catcheck.py)")
        # ssh.close()
 
        print("Processing results... (pg_catcheck.py)")
        results = extract_results(output)
        return {
            "status": "success",
            "output": output,
            **results
        }
 
    except Exception as e:
        print(f"Error: {str(e)} (pg_catcheck.py)")
        return {"status": "error", "message": str(e)}
    
def run_pg_catcheck(shell, pg_host, port, user, database, pg_password, timeout=30):
    """
    Runs the `pg_catcheck` command and captures its output, cleaning up irrelevant parts.
    """
    command = f"/usr/edb/as15/bin/pg_catcheck -h {pg_host} -p {port} -U {user} edb --verbose | sed '1,/verbose/d'\n"
    print(f"Executing command: {command.strip()} (pg_catcheck.py)")
    shell.send(command)
    time.sleep(1)  # Wait for the command prompt
 
    print("Sending pg_password... (pg_catcheck.py)")
    shell.send(pg_password + "\n")
    time.sleep(5)  # Allow time for the password to be processed and output to be generated
    print("Capturing output... (pg_catcheck.py)")
   
    output = ""
    start_time = time.time()
    while True:
        if time.time() - start_time > timeout:
            print("Timeout reached while waiting for pg_catcheck to complete. Exiting loop. (pg_catcheck.py)")
            break
        output_chunk = shell.recv(1024).decode()
        output += output_chunk
        if "done" in output.lower() or "error" in output.lower():  # Check if the command execution finished or if an error occurs
            break
 
    print("Cleaning up output... (pg_catcheck.py)")
    # Extract the section between "Password:" and the next "-bash"
    match = re.search(r"Password:\s*(.*?)\n-bash", output, re.DOTALL)
    if match:
        output = match.group(1).strip()
    else:
        output = "No valid output found or unexpected format."
 
    return output
    

 
def extract_results(output):
    """
    Extracts inconsistencies, warnings, and errors from the pg_catcheck output.
    """
    print("Extracting results from output... (pg_catcheck.py)")
    inconsistencies = re.findall(r'inconsistencies: (\d+)', output)
    warnings = re.findall(r'warnings: (\d+)', output)
    errors = re.findall(r'errors: (\d+)', output)
 
    return {
        "inconsistencies": inconsistencies[0] if inconsistencies else 0,
        "warnings": warnings[0] if warnings else 0,
        "errors": errors[0] if errors else 0
    }
 


def convert_log_to_pdf(log_output):
    pdf_filename = "pg_catcheck_output.pdf"
    c = canvas.Canvas(pdf_filename, pagesize=letter)
    width, height = letter
    margin = 50
 
    # Start writing from the top
    y_position = height - margin
    line_height = 12  # Line spacing
 
    # Split the log into lines
    lines = log_output.splitlines()
 
    for line in lines:
        if y_position < margin:  # Create a new page if no space left
            c.showPage()
            y_position = height - margin
        c.drawString(margin, y_position, line)
        y_position -= line_height
 
    c.save()
    return pdf_filename