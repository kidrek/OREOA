import glob, logging, os, subprocess
from pathlib import Path
from prefect import task
from . import utility

from os import environ as env


# Run each SYSTEM modules
@task(log_prints=True)
def run_system_modules(c_root, analyse_output_path, sanitized_name):
    regrippy_system_modules = ['antivirus', 'compname', 'gpo', 'kb', 'lastloggedon', 'lastshutdown', 'localgroups', 'localusers', 'portproxy', 'printer_ports', 'regtime', 'services', 'shimcache', 'srum', 'systeminfo', 'tasks', 'teamviewer', 'timezone', 'uninstall', 'usersids', 'version']

    for module in regrippy_system_modules:
        command = f"regrip.py --root {c_root} {module} | tee {analyse_output_path}/regrippy/{module}_{sanitized_name}.log"

        logging.info(f"Running command: {command}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        if result.returncode != 0:
            logging.error(f"Error running command : {result.stderr}")
            print(f"Error running command : {result.stderr}")


# Run each NTUSER.DAT modules
@task(log_prints=True)
def run_users_modules(c_root, analyse_output_path, sanitized_name):
    regrippy_user_modules = ['filedialogmru', 'keyboard', 'mndmru', 'mstscmru', 'printer_history', 'proxy', 'putty', 'rdphint', 'recentdocs', 'run', 'runmru', 'sysinternals', 'typedurls', 'userassist']

    for module in regrippy_user_modules:
        command = f"regrip.py --all-user-hives --root {c_root} {module} | tee {analyse_output_path}/regrippy/NTUSER_{module}_{sanitized_name}.log"

        logging.info(f"Running command: {command}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        if result.returncode != 0:
            logging.error(f"Error running command : {result.stderr}")
            print(f"Error running command : {result.stderr}")


@task(log_prints=True)
def run(input_path, analyse_output_path):
    logging.info(f"Task run regrippy: {input_path}")
    os.makedirs(f"{analyse_output_path}/regrippy", exist_ok=True)

    try:
        logging.info(f"Starting regrippy scan for {input_path}")

        # Find system root dir 
        root_system_dir = []
        system32_dir = set(glob.glob(f"{input_path}/**/**/Windows/System32", recursive=True))
        print(f"Results : {set(system32_dir)}")

        # Extract ROOT folder from system32 path
        for folder in system32_dir:
            root_system_dir.append(Path(folder).parent.parent)
            
        for folder in root_system_dir:
            sanitized_name = utility.sanitize_file_name(str(folder))
            run_system_modules.submit(folder, analyse_output_path, sanitized_name)
            run_users_modules.submit(folder, analyse_output_path, sanitized_name)


    except Exception as e:
        logging.error(f"An error occurred while running regrippy: {e}")
        print(f"An error occurred while running regrippy: {e}")

