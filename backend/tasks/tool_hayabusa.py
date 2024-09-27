import logging, os, subprocess
from prefect import task

@task(log_prints=True)
def run(input_path, analyse_output_path):
    logging.info(f"Task run hayabusa: {input_path}")
    os.makedirs(f"{analyse_output_path}/hayabusa", exist_ok=True)

    try:
        logging.info(f"Starting Hayabusa scan for {input_path}")

        docker_command = (
            f"docker run --rm --tty "
            f"--user $(id -u):$(id -g) "
            f"-v {input_path}:/opt/data:ro "
            f"-v {analyse_output_path}/hayabusa:/opt/report "
            f"hayabusa "
            f"csv-timeline "
            f"--RFC-3339 "
            f"-U "
            f"-m low "
            f"--no-wizard --no-color --quiet "
            f"-d /opt/data "
            f"-o /opt/report/timesketch-import.csv"
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
def run_pivot_keywords(input_path, analyse_output_path):
    logging.info(f"Task run hayabusa - pivot-keywords: {input_path}")
    os.makedirs(f"{analyse_output_path}/hayabusa", exist_ok=True)

    try:
        logging.info(f"Starting Hayabusa / Pivot-keywords scan for {input_path}")

        docker_command = (
            f"docker run --rm --tty "
            f"--user $(id -u):$(id -g) "
            f"-v {input_path}:/opt/data:ro "
            f"-v {analyse_output_path}/hayabusa:/opt/report "
            f"hayabusa "
            f"pivot-keywords-list "
            f"-d /opt/data "
            f"-o /opt/report/pivot-keywords "
            f"--no-wizard --no-color --quiet "

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