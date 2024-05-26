import subprocess

def run_nuclei_command(domain):
    command = ["nuclei", "-u", domain, "-es",'INFO', '-v']
    try:
        print(f"Execute nuclei {domain}")
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        with open("nuclei_log.log", "a") as f:
            f.write(result.stdout)
        print(result)
    except subprocess.CalledProcessError as e:
        print("Command failed with error:", e)