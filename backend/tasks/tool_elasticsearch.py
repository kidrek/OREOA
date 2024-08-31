import json
import os
import re
import subprocess
import requests
from prefect import task

#@task(log_prints=True)
def prepare_for_bulk(json_file_path, index_name):
    bulk_data = ''
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    for record in data:
        metadata = {"index": {"_index": index_name}}
        bulk_data += json.dumps(metadata) + '\n' + json.dumps(record) + '\n'
    return bulk_data

def sanitize_index_name(index_name):
    sanitized_name = re.sub(r'[^a-zA-Z0-9_-]', '-', index_name).lower()
    return sanitized_name

def send_bulk_data_to_elk(bulk_data_path:str, elasticsearch_host:str, elasticsearch_user:str=None, elasticsearch_password:str=None):
    elasticsearch_url = f"{elasticsearch_host}/elasticsearch/_bulk"
    command = f'curl -X POST "{elasticsearch_url}" -H "Content-Type: application/json" --data-binary @{bulk_data_path}'
    subprocess.run(command, shell=True)

#@task(log_prints=True)
def send_data_to_elk(self, directory_path:str, index_name:str, elasticsearch_host:str, elasticsearch_user:str=None, elasticsearch_password:str=None):
    bulk_folder = os.path.join(directory_path, 'bulk')
    os.makedirs(bulk_folder, exist_ok=True)

    for filename in os.listdir(directory_path):
        if filename.endswith('.json'):
            json_path = os.path.join(directory_path, filename)
            index_name = f"{index_name}"
            sanitized_index_name = sanitize_index_name(index_name)
            print(f'Sanitized index name: {sanitized_index_name}')
            bulk_data = prepare_for_bulk(json_path, sanitized_index_name)
            bulk_data_path = os.path.join(bulk_folder, f'bulk_data_{filename}')

            with open(bulk_data_path, 'w') as f:
                f.write(bulk_data)

            send_bulk_data_to_elk(bulk_data_path, elasticsearch_host, elasticsearch_user, elasticsearch_password)

@task(log_prints=True)
def add_index_pattern_to_kibana(self, kibana_host, index_prefix, index_name):
    elk_url = f'{kibana_host}'
    print(f"Adding index pattern to Kibana: {index_prefix}")
    headers = {
        'kbn-xsrf': 'true',
        'Content-Type': 'application/json'
    }
    data = {
        "data_view": {
            "title": index_prefix,
            "name": index_name,
        }
    }
    print(f'Sending request to Kibana at {elk_url}/api/data_views/data_view with data: {data}')
    response = requests.post(f'{elk_url}/api/data_views/data_view', headers=headers, json=data)
    print(f'Kibana response status code: {response.status_code}')
    if response.status_code == 200:
        print(f"Index pattern '{index_prefix}' added successfully.")
    else:
        print(f"Failed to add index pattern '{index_prefix}'. Status code: {response.status_code}")