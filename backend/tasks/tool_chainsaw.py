import glob, logging, os, subprocess
from pathlib import Path
from prefect import task
from . import utility

from dotenv import load_dotenv
from os import environ as env

## Load variables from .env file
dotenv_path = Path('.env')
load_dotenv(dotenv_path=dotenv_path)

@task(log_prints=True)
def run(evtx_path, analyse_output_filename):
    logging.info(f"Task run chainsaw: {evtx_path}")
    os.makedirs(f"{analyse_output_filename}/chainsaw", exist_ok=True)

    try:
        logging.info(f"Starting Chainsaw scan for {evtx_path}")

        docker_command = (
            f"docker run --rm --tty "
            f"--user $(id -u):$(id -g) "
            f"-v {evtx_path}:/opt/data:ro "
            f"-v {analyse_output_filename}/chainsaw:/opt/report "
            f"chainsaw hunt /opt/data "
            f"-s /opt/sigma "
            f"--mapping /opt/chainsaw/mappings/sigma-event-logs-all.yml "
            f"-r /opt/chainsaw-src/rules "
            f"--timezone UTC "
            f"--json -o /opt/report/chainsaw.log.json " 
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
