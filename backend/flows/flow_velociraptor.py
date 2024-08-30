import logging
from prefect import flow
from tasks import *

## Load variables from .env file
from dotenv import load_dotenv
from pathlib import Path
from os import environ as env
dotenv_path = Path('.env')
load_dotenv(dotenv_path=dotenv_path)

#@flow(name="velociraptor")
def run(input_path:str, output_path, sanitized_filename, password):
    logging.info('Flow Velociraptor : Starting')

    # Decompress archive
    #utility.unpack(f'{input_path}/{sanitized_filename}', f'{output_path}/{sanitized_filename}.output', password)
    utility.unpack(input_filepath = f"{input_path}/{sanitized_filename}", output_filepath = f"{output_path}/{sanitized_filename}.output", specific_file='data.zip', password = password, extraction_absolute_path=False)
    utility.unpack(input_filepath = f"{output_path}/{sanitized_filename}.output/data.zip", output_filepath = f"{output_path}/{sanitized_filename}.output", extraction_absolute_path=True)

    # Antivirus Analyse
    tool_clamav.run(output_path, sanitized_filename)

    # EVTX Analyse
    ## ZIRCOLITE
    tool_zircolite.zircolite_Windows(f'{output_path}/{sanitized_filename}.output', f'{output_path}/{sanitized_filename}.analyse')
    tool_elasticsearch.send_data_to_elk('send_data_to_elk', directory_path=f"{output_path}/{sanitized_filename}.analyse/zircolite", index_name="zircolite", elasticsearch_host=env["ES_HOST"], elasticsearch_user=env["ES_USER"], elasticsearch_password=env["ES_PASSWORD"])

    tool_chainsaw.run(f'{output_path}/{sanitized_filename}.output', f'{output_path}/{sanitized_filename}.analyse')
    tool_elasticsearch.send_data_to_elk('send_data_to_elk', directory_path=f"{output_path}/{sanitized_filename}.analyse/chainsaw", index_name="chainsaw", elasticsearch_host=env["ES_HOST"], elasticsearch_user=env["ES_USER"], elasticsearch_password=env["ES_PASSWORD"])

    #tool_elasticsearch.add_index_pattern_to_kibana('add_index_pattern_to_kibana', kibana_host=env['KIBANA_HOST'], index_prefix='zircolite*', index_name='zircolite_test')

    ## Add timefield : matches.SystemTime / source : https://www.elastic.co/docs/api/doc/kibana/v8/operation/operation-createdataviewdefaultw#operation-createdataviewdefaultw-body-application-json-elastic-api-version-2023-10-31-data_view-timefieldname
