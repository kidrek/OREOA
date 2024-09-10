import glob, logging, os, subprocess
from pathlib import Path
from prefect import task
from . import utility

## Load variables from .env file
from os import environ as env


@task(log_prints=True)
def run_log2timeline(input_path, analyse_output_path):
    logging.info(f"Task run Plaso / Log2timeline: {input_path}")
    os.makedirs(f"{analyse_output_path}/plaso", exist_ok=True)
    os.makedirs(f"{analyse_output_path}/plaso/tmp", exist_ok=True)

    try:
        logging.info(f"Starting Plaso/Log2timeline scan for {input_path}")

        docker_command = (
            f"docker run -ti "
            f"--user $(id -u):$(id -g) "
            f"-v {input_path}:/opt/data:ro "
            f"-v {analyse_output_path}/plaso:/opt/report "
            f"plaso log2timeline "
            f"-z UTC "
            f"--storage_file /opt/report/plaso_log2timeline.plaso "
            f"--partitions all "
            f"--volumes all "
            f"--logfile /opt/report/plaso_log2timeline.log.gz "
            #f"-f /opt/plaso/src/plaso/data/filter_windows.yaml "
            #f"--process_memory_limit 2048 "        
            #f"--worker_memory_limit 2048 "              # The default limit is 2147483648 (2 GiB).
            f"--temporary_directory /opt/report/tmp/ "
            f"/opt/data "
        )

        logging.info(f"Running Docker command: {docker_command}")
        print(f"Running Docker command: {docker_command}")

        result = subprocess.run(docker_command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            logging.error(f"Error running Docker command for {input_path}: {result.stderr}")
            print(f"Error running Docker command for {input_path}: {result.stderr}")
        #else:
        #    print(f"Docker command completed successfully: {result.stdout}")

    except Exception as e:
        logging.error(f"An error occurred while running Zircolite: {e}")
        print(f"An error occurred while running Zircolite: {e}")


@task(log_prints=True)
def run_psort2json(input_path, analyse_output_path):
    logging.info(f"Task run Plaso / Psort: {input_path}")
    print(f"Task run Plaso / Psort: {input_path}")
    os.makedirs(f"{analyse_output_path}/plaso", exist_ok=True)
    os.makedirs(f"{analyse_output_path}/plaso/tmp", exist_ok=True)

    try:
        docker_command = (
            f"docker run -ti "
            f"--user $(id -u):$(id -g) "
            f"-v {input_path}:/opt/data/timeline.plaso:ro "
            f"-v {analyse_output_path}/plaso:/opt/report "
            f"plaso psort "
            f"--logfile /opt/report/plaso_psort.log.gz "
            f"-o json_line "
            f"-w /opt/report/plaso_psort.json "
            f"--temporary_directory /opt/report/tmp/ "
            f"-q /opt/data/timeline.plaso"
        )

        logging.info(f"Running Docker command: {docker_command}")
        print(f"Running Docker command: {docker_command}")

        result = subprocess.run(docker_command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            logging.error(f"Error running Docker command for {input_path}: {result.stderr}")
            print(f"Error running Docker command for {input_path}: {result.stderr}")
        #else:
        #    print(f"Docker command completed successfully: {result.stdout}")

    except Exception as e:
        logging.error(f"An error occurred while running Zircolite: {e}")
        print(f"An error occurred while running Zircolite: {e}")


@task(log_prints=True)
def run_psort2elasticsearch(input_path, analyse_output_path):
    logging.info(f"Task run Plaso / Psort: {input_path}")
    print(f"Task run Plaso / Psort: {input_path}")
    os.makedirs(f"{analyse_output_path}/plaso", exist_ok=True)
    os.makedirs(f"{analyse_output_path}/plaso/tmp", exist_ok=True)

    try:
        docker_command = (
            f"docker run -ti "
            f"--user $(id -u):$(id -g) "
            f"-v {input_path}:/opt/data/:ro "
            f"-v {analyse_output_path}/plaso:/opt/report "
            f"plaso psort "
            f"-o opensearch "
            f"--index_name='plaso_log2timeline2' "
            f"--opensearch-server={env['ES_HOST']} "
            f"--opensearch-port={env['ES_PORT']} "
            f"--opensearch-user={env['ES_USER']} "
            f"--opensearch-password={env['ES_PASSWORD']} "
            f"--opensearch-mappings /opt/plaso/plaso.mappings "
            f"--logfile /opt/report/plaso_psort.log.gz "
            f"--temporary_directory /opt/report/tmp/ "
            f"-q /opt/report/plaso_log2timeline.plaso"
        )


        logging.info(f"Running Docker command: {docker_command}")
        print(f"Running Docker command: {docker_command}")

        result = subprocess.run(docker_command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            logging.error(f"Error running Docker command for {input_path}: {result.stderr}")
            print(f"Error running Docker command for {input_path}: {result.stderr}")
        #else:
        #    print(f"Docker command completed successfully: {result.stdout}")

    except Exception as e:
        logging.error(f"An error occurred while running Zircolite: {e}")
        print(f"An error occurred while running Zircolite: {e}")


@task(log_prints=True)
def run_psort2timesketch(input_path, analyse_output_path):
    logging.info(f"Task run Plaso / Psort: {input_path}")
    print(f"Task run Plaso / Psort: {input_path}")
    os.makedirs(f"{analyse_output_path}/plaso", exist_ok=True)
    os.makedirs(f"{analyse_output_path}/plaso/tmp", exist_ok=True)

    try:
        docker_command = (
            f"docker run -ti "
            f"--user $(id -u):$(id -g) "
            f"-v {input_path}:/opt/data/:ro "
            f"-v {analyse_output_path}/plaso:/opt/report "
            f"plaso psort "
            f"-o opensearch_ts "
            f"--index_name='plaso_psort_timesketch' "
            f"--opensearch-server={env['TIMESKETCH_HOST']} "
            f"--opensearch-port={env['TIMESKETCH_PORT']} "
            f"--opensearch-user={env['TIMESKETCH_USER']} "
            f"--opensearch-password={env['TIMESKETCH_PASSWORD']} "
            f"--opensearch-mappings /opt/plaso/plaso.mappings "
            f"--logfile /opt/report/plaso_psort.log.gz "
            f"--temporary_directory /opt/report/tmp/ "
            f"-q /opt/report/plaso_log2timeline.plaso"
        )


        logging.info(f"Running Docker command: {docker_command}")
        print(f"Running Docker command: {docker_command}")

        result = subprocess.run(docker_command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            logging.error(f"Error running Docker command for {input_path}: {result.stderr}")
            print(f"Error running Docker command for {input_path}: {result.stderr}")
        #else:
        #    print(f"Docker command completed successfully: {result.stdout}")

    except Exception as e:
        logging.error(f"An error occurred while running Zircolite: {e}")
        print(f"An error occurred while running Zircolite: {e}")

