import logging, os, subprocess
from prefect import task


@task(log_prints=True)
def run(scan_output_path, sanitized_filename):
    logging.info("Running ClamAV Analysis...", 60)
    image_name = "clamav-image"

    docker_command = (
        f"docker run -it --rm "
        f"--user $(id -u):$(id -g) --entrypoint /init-unprivileged "
        f"-v {scan_output_path}:/scandir "
        f"clamav/clamav:unstable "
        f"clamscan "
        f"-l /scandir/{sanitized_filename}.analyse/clamav.log " 
        f"-r -i --quiet "
        f"/scandir/{sanitized_filename}.output "
    )


    print(docker_command)
    result = subprocess.run(docker_command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        logging.error(f"Error running Docker command : {result.stderr}")
        print(f"Error running Docker command : {result.stderr}")
    else:
        print(f"Docker command completed successfully: {result.stdout}")
