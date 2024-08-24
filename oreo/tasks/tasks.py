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
             name='task_find_evtx',
             priority=2,
             max_retry=5,
             soft_time_limit=600)
def task_find_evtx(self, filepath:str):
    logging.info(f'Task FindEVTX : Call task')
    dir_evtx=[]
    for pattern in env['EVTX_LOCATION_PATTERN'].split(','):
        dir_evtx.append(run_find_directory.init(pattern, filepath))
    logging.info(f"Result: {dir_evtx}")


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

        # 1st task : generate hash
        task_sha256.delay(f"{original_path}/{sanitize_filename}",)

        # 2nd task : Workflow by evidence type
        evidence_type = determine_evidence_type(original_filename)
        if evidence_type == "VELOCIRAPTOR":
            task_extract_files.delay(f"{original_path}/{sanitize_filename}", f"{env['SCAN_OUTPUT_PATH']}/{sanitize_filename}_extracted", env['VELOCIRAPTOR_EVIDENCE_PASSWORD'])

            # Create a single task
            """
            tasks = [app.send_task('task_sha256', args=(f"{ARTIFACT_PATH}/{sanitize_filename}",), retry=True),
                        app.send_task('task_extract_files', args=(f"{ARTIFACT_PATH}/{sanitize_filename}", f"{SCAN_OUTPUT_PATH}/{sanitize_filename}_extracted", env['VELOCIRAPTOR_EVIDENCE_PASSWORD']), retry=True)]
            """
        else:
            if evidence_type == "other":
                if filename.endswith('.zip') or filename.endswith('.7z'):
                    task_extract_files.delay(f"{original_path}/{sanitize_filename}", f"{env['SCAN_OUTPUT_PATH']}/{sanitize_filename}_extracted")
                else:
                    task_move_file.delay(filename, f"{env['SCAN_OUTPUT_PATH']}/{sanitize_filename}",)
                

        # X task : Find EVTX
        task_find_evtx.delay(f"{env['SCAN_OUTPUT_PATH']}/{sanitize_filename}_extracted",)


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