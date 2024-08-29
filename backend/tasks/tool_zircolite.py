import glob, logging, os, subprocess, time
from pathlib import Path
from prefect import task
from . import utility

from dotenv import load_dotenv
from os import environ as env

## Load variables from .env file
dotenv_path = Path('.env')
load_dotenv(dotenv_path=dotenv_path)

@task(log_prints=True)
def zircolite_Windows(evtx_path, analyse_output_filename):
    logging.info(f"Task run zircolite: {evtx_path}")
    os.makedirs(f"{analyse_output_filename}/zircolite", exist_ok=True)

    try:
        logging.info(f"Starting Zircolite scan for {evtx_path}")
        evtx_files = []

        # Find all evtx files 
        print(f"EVTX_Pattern: env['EVTX_PATTERN']")
        for pattern in env['EVTX_PATTERN'].split(','):
            evtx_files = evtx_files + glob.glob(f"{evtx_path}/**/*{pattern}", recursive=True)

        # Analyse all identified files. 
        # Use Zircolite file by file to reduce crash possibility 
        if len(evtx_files) > 0:
            for evtx_file in evtx_files:
                intput_evtx_directory = Path(evtx_file).parent
                input_evtx_filename = Path(evtx_file).name


                # Sanitize name
                ## Necessaire pour les fichiers (avec espace dans le nom) tels que : Microsoft-Windows-Windows Firewall With Advanced Security%254ConnectionSecurity.evtx
                sanitized_name = utility.sanitize_file_name(input_evtx_filename)
                if input_evtx_filename != sanitized_name:
                    utility.move_file(f"{intput_evtx_directory}/{input_evtx_filename}", f"{intput_evtx_directory}/{sanitized_name}",)
                    time.sleep(0.1)
                    input_evtx_filename = sanitized_name

                output_filename = f"{input_evtx_filename}_detection.json"

                print(intput_evtx_directory)
                print(input_evtx_filename)
                print(output_filename)

                docker_command = (
                    f"docker run --rm --tty "
                    f"--user $(id -u):$(id -g) "
                    f"-v {intput_evtx_directory}:/case/input:ro "
                    f"-v {analyse_output_filename}/zircolite:/case/output "
                    f"wagga40/zircolite "
                    f"--ruleset rules/rules_windows_generic_full.json --evtx /case/input/{input_evtx_filename} "
                    f"-o /case/output/{output_filename} " 
                    f"-l /case/output/zircolite.log -t /case/output/zircolite.tmp"
                )

                logging.info(f"Running Docker command: {docker_command}")
                print(f"Running Docker command: {docker_command}")

                result = subprocess.run(docker_command, shell=True, capture_output=True, text=True)
                if result.returncode != 0:
                    logging.error(f"Error running Docker command for {evtx_path}: {result.stderr}")
                    print(f"Error running Docker command for {evtx_path}: {result.stderr}")
                else:
                    print(f"Docker command completed successfully: {result.stdout}")

    except Exception as e:
        logging.error(f"An error occurred while running Zircolite: {e}")
        print(f"An error occurred while running Zircolite: {e}")
