import os
import subprocess
from prefect import task

@task(log_prints=True)
def import_dashboard(directory_path:str, kibana_host:str, kibana_user:str=None, kibana_password:str=None):
    print(directory_path)
    for filename in os.listdir(directory_path):
        if filename.endswith('.ndjson'):
            command = f'curl -X POST "{kibana_host}/api/saved_objects/_import?overwrite=true" -H "kbn-xsrf: true" --form file=@{directory_path}/{filename}'
            subprocess.run(command, shell=True)
            