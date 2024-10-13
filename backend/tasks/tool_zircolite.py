import glob, logging, os, subprocess
from pathlib import Path
from prefect import task
from . import utility

from os import environ as env


@task(log_prints=True)
def run2Timesketch(input_path, analyse_output_path):
    logging.info(f"Task run zircolite: {input_path}")
    os.makedirs(f"{analyse_output_path}/zircolite", exist_ok=True)

    try:
        logging.info(f"Starting Zircolite scan for {input_path}")
        evtx_files = []

        # Find all evtx files 
        extensions = env['EVTX_PATTERN'].split(',')
        evtx_files = evtx_files + [file for file in Path(input_path).rglob('*.*') if file.suffix in extensions]

        # Analyse all identified files. 
        # Use Zircolite file by file to reduce crash possibility 
        if len(evtx_files) > 0:
            for evtx_file in evtx_files:
                print(f"Analyse : {evtx_file}")
                intput_evtx_directory = Path(evtx_file).parent
                input_evtx_filename = Path(evtx_file).name.replace(' ','\ ')

                # Sanitize name
                ## Necessaire pour les fichiers (avec espace dans le nom) tels que : Microsoft-Windows-Windows Firewall With Advanced Security%254ConnectionSecurity.evtx
                sanitized_name = utility.sanitize_file_name(input_evtx_filename)
                output_filename = f"{sanitized_name}_detection.json"

                docker_command = (
                    f"docker run --rm --tty "
                    f"--platform linux/amd64 "
                    f"--user $(id -u):$(id -g) "
                    f"-v {intput_evtx_directory}:/case/input:ro "
                    f"-v {analyse_output_path}/zircolite:/case/output "
                    f"wagga40/zircolite:2.20.0 "
                    f"--ruleset rules/rules_windows_generic_full.json --evtx /case/input/{input_evtx_filename} "
                    f"--template templates/exportForTimesketch.tmpl "
                    f"--templateOutput /case/output/timesketch.json " 
                    f"-o /case/output/{output_filename} "
                    f"-l /case/output/zircolite.log -t /case/output/zircolite.tmp"
                )

                logging.info(f"Running Docker command: {docker_command}")
                print(docker_command)
                result = subprocess.run(docker_command, shell=True, capture_output=True, text=True)

                if result.returncode != 0:
                    logging.error(f"Error running Docker command for {input_path}: {result.stderr}")
                    print(f"Error running Docker command for {input_path}: {result.stderr}")
                else:
                    print(f"Docker command completed successfully: {result.stdout}")

    except Exception as e:
        logging.error(f"An error occurred while running Zircolite: {e}")
        print(f"An error occurred while running Zircolite: {e}")
