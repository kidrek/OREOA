import logging, os, re, time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from prefect import task
from tasks import *
from flows import *

## Load variables from .env file
from dotenv import load_dotenv
from pathlib import Path
from os import environ as env
dotenv_path = Path('.env')
load_dotenv(dotenv_path=dotenv_path)


## Class to handle filesystem events
class MyHandler(FileSystemEventHandler):
    def on_created(self, event):

        if not event.src_path.endswith(('.md5', '.sha256', '.sha1')):
            logging.info(f'File {event.src_path} has been created')

            original_filename = Path(event.src_path).name
            original_path = Path(event.src_path).parent

            # Sanitize name
            sanitized_name = utility.sanitize_file_name(original_filename)
            if original_filename != sanitized_name:
                utility.move_file(f"{original_path}/{original_filename}", f"{original_path}/{sanitized_name}",)

            # Generate Hash
            utility.generate_hash(hash=env['HASH_ALGO'], filepath=f"{original_path}/{sanitized_name}")

            # Determine evidence type
            evidence_type = utility.determine_evidence_type(original_filename)


            # Define output and analyse folders for this artifacts
            scan_output_filename = f"{sanitized_name}.output"
            analyse_output_filename = f"{sanitized_name}.analyse"
            os.makedirs(f"{env['SCAN_OUTPUT_PATH']}/{analyse_output_filename}", exist_ok=True)


            if evidence_type == "velociraptor":
                print(f"Password Velociraptor: {env['VELOCIRAPTOR_EVIDENCE_PASSWORD']} / longueur: {len(env['VELOCIRAPTOR_EVIDENCE_PASSWORD'])}")
                flow_velociraptor.run(input_path = f"{env['ARTIFACT_INPUT_PATH']}", output_path = f"{env['SCAN_OUTPUT_PATH']}", sanitized_filename = f"{sanitized_name}" , password = env['VELOCIRAPTOR_EVIDENCE_PASSWORD'])
            else:
                if evidence_type == "other":
                    if sanitized_name.endswith('.zip') or sanitized_name.endswith('.7z'):
                        utility.unpack(input_file = f"{original_path}/{sanitized_name}", output_file = f"{env['SCAN_OUTPUT_PATH']}/{scan_output_filename}", password = '', nested=False)
                    else:
                        utility.move_file(sanitized_name, f"{env['SCAN_OUTPUT_PATH']}/{sanitized_name}",)

                flow_common.run(scan_output_filename, analyse_output_filename)
            ## Setup Kibana dashboards
            tool_kibana.import_dashboard( directory_path='../frontend/kibana_dashboard', kibana_host=env['KIBANA_HOST'], kibana_user=env['KIBANA_USER'], kibana_password=env['KIBANA_PASSWORD'])


# Listen any activity on ARTIFACT_INPUT_PATH directory
if __name__=="__main__":
    logging.info(f"Running daemon")

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
