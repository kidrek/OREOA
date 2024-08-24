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
            if original_filename != sanitize_filename:
                app.send_task('task_move_file', args=(event.src_path, f"{ARTIFACT_PATH}/{sanitize_filename}",), retry=True)

            # 1st task : generate hash
            app.send_task('task_sha256', args=(f"{ARTIFACT_PATH}/{sanitize_filename}",), retry=True)
            
            # 2nd task : Workflow by evidence type
            evidence_type = determine_evidence_type(original_filename)
            if evidence_type == "VELOCIRAPTOR":
                app.send_task('task_extract_files', args=(f"{ARTIFACT_PATH}/{sanitize_filename}", f"{SCAN_OUTPUT_PATH}/{sanitize_filename}_extracted", env['VELOCIRAPTOR_EVIDENCE_PASSWORD']), retry=True)



def determine_evidence_type(filename):
    # Determine evidence type
    if re.match(VELOCIRAPTOR_EVIDENCE_PATTERN, filename, re.IGNORECASE):
        evidence_type = "VELOCIRAPTOR"
        print("Velociraptor evidence")
    else:
        evidence_type = "other"    
    return evidence_type

# Function to replace all characters, except 'a-zA-Z0-9._-' by -
def sanitize_file_name(filename):
    sanitized_name = re.sub(r'[^a-zA-Z0-9._-]', '-', filename).lower()
    return sanitized_name
    

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
