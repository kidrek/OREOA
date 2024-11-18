import logging, os, re, time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from backend.tasks import utility
from backend.flows import *

## Load variables from .env file
from dotenv import load_dotenv
from pathlib import Path
from os import environ as env

## Class to handle filesystem events
class MyHandler(FileSystemEventHandler):
    def on_created(self, event):

        if not event.src_path.endswith(('.md5', '.sha256', '.sha1')):
            logging.info(f'File {event.src_path} has been created')

            original_filename = Path(event.src_path).name

            # Sanitize name
            sanitized_name = utility.sanitize_file_name(original_filename)

            # Run - Flow common
            flow_common.run(input_path=event.src_path,analyse_path=f"{env['SCAN_OUTPUT_PATH']}/{sanitized_name}_extracted")



# Listen any activity on ARTIFACT_INPUT_PATH directory
if __name__=="__main__":
    logging.info("Running daemon")

    # Load .env preferences
    env_path = Path('.env')
    load_dotenv(dotenv_path=env_path)

    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path=env['ARTIFACT_INPUT_PATH'], recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
