import hashlib, logging, re
from pathlib import Path

from celery import shared_task
from celery import chain
from . import *             # Need to declare all python scripts in __init__.py

from dotenv import load_dotenv
from os import environ as env

## Load variables from .env file
dotenv_path = Path('.env')
load_dotenv(dotenv_path=dotenv_path)



@shared_task(bind=True, 
             name='task_extract_files', 
             priority=5,
             max_retry=5,
             soft_time_limit=600)
def task_extract_files(self, filepath:str, output_filepath:str, password:str=None):
    logging.info(f'Task Extract files : Call task')
    run_extract.run(filepath, output_filepath, password, nested=False)

@shared_task(bind=True, 
             name='task_process_evtx',
             priority=2,
             max_retry=5,
             soft_time_limit=600)
def task_process_evtx(self, input_path:str, analyse_output_filename:str):
    logging.info(f'Task Process EVTX : Call task')

    """
    dir_evtx=[]
    for pattern in env['EVTX_PATTERN'].split(','):
        dir_evtx = dir_evtx + run_find_files.find_files(pattern, input_path)
    logging.info(f"Result: {dir_evtx}")
    logging.info(f'Task FindEVTX : filepath: {input_path}')

    count = 0
    for dir in dir_evtx:
        run_zircolite.zircolite_Windows(dir, analyse_output_filename)
    """
    run_zircolite.zircolite_Windows(input_path, f"{analyse_output_filename}/zircolite")

    from oreo.celery import app
    app.send_task('add_index_pattern_to_kibana', args=(env['KIBANA_HOST'],'zircolite*','zircolite'))
    ## Add timefiel : matches.SystemTime / source : https://www.elastic.co/docs/api/doc/kibana/v8/operation/operation-createdataviewdefaultw#operation-createdataviewdefaultw-body-application-json-elastic-api-version-2023-10-31-data_view-timefieldname
    
    app.send_task('send_data_to_elk', args=(f"{analyse_output_filename}/zircolite", "zircolite", env["ES_HOST"],env["ES_USER"], env["ES_PASSWORD"]))

@shared_task(bind=True, 
             name='task_copy_file',
             priority=0,
             max_retry=5,
             soft_time_limit=10)
def task_copy_file(self, filepath:str, output_filepath:str):
    logging.info(f'Task CopyFile : Call task')
    run_copy_file.run(filepath, output_filepath)


@shared_task(bind=True, 
             name='task_move_file',
             priority=0,
             max_retry=5,
             soft_time_limit=10)
def task_move_file(self, filepath:str, output_filepath:str):
    logging.info(f'Task MoveFile : Call task')
    run_move_file.run(filepath, output_filepath)


@shared_task(bind=True, 
             name='task_sha256',
             priority=2,
             max_retry=5,
             soft_time_limit=600)
def task_sha256(self, filepath:str):
    logging.info(f'Task SHA256 : Call task')
    run_sha256.sha256_generate(filepath)
    

@shared_task(bind=True, name='task_init')
def task_init(self, filename):
    logging.info(f'Task INIT : Call task')
    if not filename.endswith('.sha256'):
        original_filename = Path(filename).name
        original_path = Path(filename).parent

        # Sanitize filename to remove space, etc...
        sanitize_filename = sanitize_file_name(original_filename)
        if original_filename != sanitize_filename:
            task_move_file.delay(filename, f"{original_path}/{sanitize_filename}",)

        # Define output and analyse folders for this artifacts
        scan_output_filename = f"{sanitize_filename}.output"
        analyse_output_filename = f"{sanitize_filename}.analyse"

        # 1st task : generate hash
        task_sha256.delay(f"{original_path}/{sanitize_filename}",)

        # 2nd task : Workflow by evidence type
        evidence_type = determine_evidence_type(original_filename)
        if evidence_type == "VELOCIRAPTOR":
            task_extract_files.delay(f"{original_path}/{sanitize_filename}", f"{env['SCAN_OUTPUT_PATH']}/{scan_output_filename}", env['VELOCIRAPTOR_EVIDENCE_PASSWORD'])

            # Create a single task
            """
            tasks = [app.send_task('task_sha256', args=(f"{ARTIFACT_PATH}/{sanitize_filename}",), retry=True),
                        app.send_task('task_extract_files', args=(f"{ARTIFACT_PATH}/{sanitize_filename}", f"{SCAN_OUTPUT_PATH}/{sanitize_filename}_extracted", env['VELOCIRAPTOR_EVIDENCE_PASSWORD']), retry=True)]
            """
        else:
            if evidence_type == "other":
                if filename.endswith('.zip') or filename.endswith('.7z'):
                    task_extract_files.delay(f"{original_path}/{sanitize_filename}", f"{env['SCAN_OUTPUT_PATH']}/{scan_output_filename}")
                else:
                    task_move_file.delay(filename, f"{env['SCAN_OUTPUT_PATH']}/{sanitize_filename}",)
                

        # X task : Find EVTX
        task_process_evtx.delay(f"{env['SCAN_OUTPUT_PATH']}/{scan_output_filename}", f"{env['SCAN_OUTPUT_PATH']}/{analyse_output_filename}")


# Function to replace all characters, except 'a-zA-Z0-9._-' by -
def sanitize_file_name(filename):
    sanitized_name = re.sub(r'[^a-zA-Z0-9._-]', '-', filename).lower()
    return sanitized_name


def determine_evidence_type(filename):
    # Determine evidence type
    if re.match(env['VELOCIRAPTOR_EVIDENCE_PATTERN'], filename, re.IGNORECASE):
        evidence_type = "VELOCIRAPTOR"
        print("Velociraptor evidence")
    else:
        evidence_type = "other"    
    return evidence_type