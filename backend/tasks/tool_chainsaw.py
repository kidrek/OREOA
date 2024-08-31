import glob, logging, os, subprocess
from pathlib import Path
from prefect import task
from . import utility


@task(log_prints=True)
def run(input_path, analyse_output_path):
    logging.info(f"Task run chainsaw: {input_path}")
    os.makedirs(f"{analyse_output_path}/chainsaw", exist_ok=True)

    try:
        logging.info(f"Starting Chainsaw scan for {input_path}")

        docker_command = (
            f"docker run --rm --tty "
            f"--user $(id -u):$(id -g) "
            f"-v {input_path}:/opt/data:ro "
            f"-v {analyse_output_path}/chainsaw:/opt/report "
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
            logging.error(f"Error running Docker command for {input_path}: {result.stderr}")
            print(f"Error running Docker command for {input_path}: {result.stderr}")
        else:
            print(f"Docker command completed successfully: {result.stdout}")

    except Exception as e:
        logging.error(f"An error occurred while running Zircolite: {e}")
        print(f"An error occurred while running Zircolite: {e}")


# SHIMCACHE ANALYSE
# docker run --rm --tty --user $(id -u):$(id -g) -v /home/kidrek/Documents/scripts/PCSIRT/PCSIRT_sources/scans_output/collection-mlap-0dvjoxddca_mgsi_mg_com_fr-2024-08-12t12_36_13_02_00--copy-.zip.output/uploads/auto/C%3A/Windows/:/opt/data:ro -v /home/kidrek/Documents/scripts/PCSIRT/PCSIRT_sources/scans_output/collection-mlap-0dvjoxddca_mgsi_mg_com_fr-2024-08-12t12_36_13_02_00--copy-.zip.analyse/chainsaw:/opt/report chainsaw analyse shimcache /opt/data/System32/config/SYSTEM  -a /opt/data/appcompat/Programs/Amcache.hve  --output /opt/report/chainsaw_shimcache.log


# SRUM ANALYSE
# docker run --rm --tty --user $(id -u):$(id -g) -v /home/kidrek/Documents/scripts/PCSIRT/PCSIRT_sources/scans_output/collection-mlap-0dvjoxddca_mgsi_mg_com_fr-2024-08-12t12_36_13_02_00--copy-.zip.output/uploads/auto/C%3A/Windows/System32/:/opt/data:ro -v /home/kidrek/Documents/scripts/PCSIRT/PCSIRT_sources/scans_output/collection-mlap-0dvjoxddca_mgsi_mg_com_fr-2024-08-12t12_36_13_02_00--copy-.zip.analyse/chainsaw:/opt/report chainsaw analyse srum --software /opt/data/config/SOFTWARE /opt/data/sru/SRUDB.dat  -q  --stats-only | less