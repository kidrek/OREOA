import logging, os, subprocess
from prefect import task
from os import environ as env

@task(log_prints=True)
def run_upload(input_filename:str):
    logging.info(f"Task run timesketch upload: {input_filename}")

    try:
        logging.info(f"Starting timesketch upload for {input_filename}")

        docker_command = (
            f"docker exec "
            f"timesketch-worker "
            f"/bin/bash -c "
            f"\"timesketch_importer "
            f"-u {env['TIMESKETCH_USER']} -p {env['TIMESKETCH_USER']} --host http://timesketch-web:5000 "     # Timesketch URI is docker internal URI
            f"--timeline_name {input_filename} "
            f"--sketch_name {env['TIMESKETCH_DEFAULT_SKETCH_NAME']} "
            f"/usr/share/timesketch/upload/{input_filename}.plaso\" "
        )

        ## docker exec timesketch-worker /bin/bash -c "timesketch_importer -u secubian -p secubian --host http://timesketch-web:5000 --timeline_name test --sketch_id 17 /usr/share/timesketch/upload/plaso_log2timeline.plaso"

        logging.info(f"Running Docker command: {docker_command}")
        print(f"Running Docker command: {docker_command}")

        result = subprocess.run(docker_command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            logging.error(f"Error running Docker command for {input_filename}: {result.stderr}")
            print(f"Error running Docker command for {input_filename}: {result.stderr}")
        #else:
        #    print(f"Docker command completed successfully: {result.stdout}")

    except Exception as e:
        logging.error(f"An error occurred while running Zircolite: {e}")
        print(f"An error occurred while running Zircolite: {e}")
