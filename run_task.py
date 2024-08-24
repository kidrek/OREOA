import hashlib, logging, re, subprocess, time
from os import environ as env
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from oreo.celery import app

from dotenv import load_dotenv
from pathlib import Path

## Load variables from .env file
dotenv_path = Path('.env')
load_dotenv(dotenv_path=dotenv_path)



class MyHandler(FileSystemEventHandler):
    def on_created(self, event):
        print(f'File {event.src_path} has been created')
        if not event.src_path.endswith('.sha256'):
            original_filename = Path(event.src_path).name

            # Sanitize filename to remove space, etc...
            sanitize_filename = sanitize_file_name(original_filename)
            move_input_artifacts(event.src_path, f"{ARTIFACT_PATH}/{sanitize_filename}")
            time.sleep(0.1)

            # 1st task : generate hash
            app.send_task('task_sha256', args=(f"{ARTIFACT_PATH}/{sanitize_filename}",), retry=True)

            # 2nd task : Workflow by evidence type
            evidence_type = determine_evidence_type(original_filename)
            if evidence_type == "VELOCIRAPTOR":
                app.send_task('task_extract_files', args=(f"{ARTIFACT_PATH}/{sanitize_filename}", f"{SCAN_OUTPUT_PATH}/{sanitize_filename}_extracted", env['VELOCIRAPTOR_EVIDENCE_PASSWORD']), retry=True)
                #task_extract = app.signature('task_extract_files', args=(original_filename, f"{SCAN_OUTPUT_PATH}/{sanitize_filename}_extracted", env['VELOCIRAPTOR_EVIDENCE_PASSWORD']), retry=True)
                #tasks = (task_extract)()



def determine_evidence_type(filename):
    # Determine evidence type
    if re.match(VELOCIRAPTOR_EVIDENCE_PATTERN, filename):
        evidence_type = "VELOCIRAPTOR"
        print("Velociraptor evidence")
    else:
        evidence_type = "other"    
    return evidence_type

# Function to replace all characters, except 'a-zA-Z0-9._-' by -
def sanitize_file_name(filename):
    sanitized_name = re.sub(r'[^a-zA-Z0-9._-]', '-', filename).lower()
    return sanitized_name


def move_input_artifacts(source_filepath, dst_filepath):
    mv_command = [
        'mv', 
        f'{source_filepath}',
        f'{dst_filepath}'
    ]

    try:
        result = subprocess.run(mv_command, check=True, capture_output=True, text=True)
        print(f"Move output: {result.stdout}")
        if result.stderr:
            print(f"Move error: {result.stderr}")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")
        raise e

if __name__ == "__main__":
    logging.info(f"Running daemon")

    ## DEBUG
    #oreo.celery.debug_task.delay()

    ## Set variables
    ARTIFACT_PATH = env['ARTIFACT_PATH']
    SCAN_OUTPUT_PATH = env['SCAN_OUTPUT_PATH']
    VELOCIRAPTOR_EVIDENCE_PATTERN = env['VELOCIRAPTOR_EVIDENCE_PATTERN']

    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path=ARTIFACT_PATH, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()



