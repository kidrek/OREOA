import glob, logging, os, subprocess
from pathlib import Path
from prefect import task

from . import utility

from os import environ as env


# Run each SYSTEM modules
@task(log_prints=False)
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
@task(log_prints=False)
def run_users_modules(c_root, analyse_output_path, sanitized_name):
    regrippy_user_modules = ['filedialogmru', 'keyboard', 'mndmru', 'mstscmru', 'printer_history', 'proxy', 'putty', 'rdphint', 'recentdocs', 'run', 'runmru', 'sysinternals', 'typedurls', 'userassist']

    for module in regrippy_user_modules:
        command = f"regrip.py --all-user-hives --root {c_root} {module} | tee {analyse_output_path}/regrippy/NTUSER_{module}_{sanitized_name}.log"

        logging.info(f"Running command: {command}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        if result.returncode != 0:
            logging.error(f"Error running command : {result.stderr}")
            print(f"Error running command : {result.stderr}")


def find_registry(root_directory, pattern):
  for f in root_directory.glob(f"**/**/{pattern}"):
     if pattern in str(f):
        return(str(f))

@task(log_prints=True)
def run_regrippy(input_path, analyse_output_path):
    logging.info(f"Task run regrippy: {input_path}")
    os.makedirs(f"{analyse_output_path}/regrippy", exist_ok=True)

    try:
        logging.info(f"Starting regrippy scan for {input_path}")

        # Find system root dir 
        root_directory_input = Path(input_path)
        pattern = '/Windows/System32/config/SAM'
        root_directory_windows = ''
        registry_path = []
        res = find_registry(root_directory_input, pattern)
        if res != None:
          registry_path.append(res)
        if len(registry_path) == 0:
          res = find_registry(root_directory_input, pattern.lower())
          if res != None:
            registry_path.append(res)
        if len(registry_path) == 0:
          res = find_registry(root_directory_input, pattern.upper())
          if res != None:
            registry_path.append(res)

        # Extract ROOT folder from system32 path
        if len(registry_path) > 0:
          root_directory_windows = registry_path[0].lower().split(pattern.lower())[0]
          logging.info(f'System root of Microsoft Windows : {root_directory_windows}')

          sanitized_name = utility.sanitize_file_name(str(root_directory_windows))
          logging.info(f'Task regrippy: Launch System modules')
          run_system_modules.submit(root_directory_windows, analyse_output_path, sanitized_name)
          logging.info(f'Task regrippy: Launch User modules')
          run_users_modules.submit(root_directory_windows, analyse_output_path, sanitized_name)


    except Exception as e:
        logging.error(f"An error occurred while running regrippy: {e}")
        print(f"An error occurred while running regrippy: {e}")

