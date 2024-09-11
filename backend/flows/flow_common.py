import datetime, logging, os, stat
from backend.tasks import *
from backend.flows import flow_evidence_device, flow_evidence_folder, flow_evidence_velociraptor
from pathlib import Path


# Load flow from prefect
from prefect import flow
from prefect_dask.task_runners import DaskTaskRunner

## Load variables from .env file
from os import environ as env



def run(input_path, analyse_path):
    logging.info('Flow Common : Starting')

    # Create analyse_path
    analyse_output_filename = f"{analyse_path}/analyse"
    os.makedirs(f"{analyse_path}", exist_ok=True)
    os.makedirs(f"{analyse_output_filename}", exist_ok=True)

    if os.path.isdir(input_path):
        evidence_type = "folder"
        # Run - prefect flow / investigation_flow
        flow_evidence_folder.investigate(input_path, analyse_output_filename)

    elif stat.S_ISBLK(os.stat(input_path).st_mode):
        evidence_type = "device"
        # Run - prefect flow / investigation_flow
        flow_evidence_device.investigate(input_path, analyse_output_filename)

    else:
        if os.path.isfile(input_path):
            evidence_type = "file"
            original_filename = Path(input_path).name
            original_path = Path(input_path).parent

            # Sanitize name
            sanitized_name = utility.sanitize_file_name(original_filename)
            if original_filename != sanitized_name:
                utility.move_file(f"{original_path}/{original_filename}", f"{original_path}/{sanitized_name}",)

            # Generate Hash
            utility.generate_hash(hash=env['HASH_ALGO'], filepath=f"{original_path}/{sanitized_name}")

            # Define output and analyse folders for this artifacts
            scan_output_filename = f"{analyse_path}/output"
            os.makedirs(f"{scan_output_filename}", exist_ok=True)

            # Determine evidence type
            evidence_type = utility.determine_evidence_type(original_filename)

            # Handle evidence type
            if evidence_type == "velociraptor":
                #flow_evidence_velociraptor.run(input_path = f"{original_path}/{sanitized_name}", output_path = f"{scan_output_filename}", sanitized_filename = f"{sanitized_name}" , password = env['VELOCIRAPTOR_EVIDENCE_PASSWORD'])

                # Run - prefect flow / investigation_flow
                flow_evidence_folder.investigate(scan_output_filename, analyse_output_filename)


    # Once tools finished, process results
    process_result(sanitized_name, scan_output_filename, analyse_output_filename)


@flow(task_runner=DaskTaskRunner(cluster_kwargs={"processes": False}))
def process_result(sanitized_name, scan_output_filename, analyse_output_filename):
    ### TODO - Création d'un workflow pour distribuer les tâches
    if os.path.isdir(env['TIMESKETCH_UPLOAD_PATH']) :

        # Copy plaso file to TIMESKETCH_UPLOAD_PATH
        if os.path.isfile(f"{analyse_output_filename}/plaso/plaso_log2timeline.plaso"):
            utility.copy_file(f"{analyse_output_filename}/plaso/plaso_log2timeline.plaso", f"{env['TIMESKETCH_UPLOAD_PATH']}/{sanitized_name}.plaso")

        # Copy hayabusa timeline to TIMESKETCH_UPLOAD_PATH
        if os.path.isfile(f"{analyse_output_filename}/hayabusa/timesketch-import.csv"):
            utility.copy_file(f"{analyse_output_filename}/hayabusa/timesketch-import.csv", f"{env['TIMESKETCH_UPLOAD_PATH']}/{sanitized_name}_hayabusa.csv")


        # TODO / Import plaso file with specific sketch name, and timeline name
        # set sketch as case_id
        tool_timesketch.run_upload.submit(f"{sanitized_name}.plaso")
        tool_timesketch.run_upload.submit(f"{sanitized_name}_hayabusa.csv")


    # TODO / Generate HASH for all of analyses files
