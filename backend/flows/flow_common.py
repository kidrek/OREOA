import logging
from tasks import *

## Load variables from .env file
from dotenv import load_dotenv
from pathlib import Path
from os import environ as env
dotenv_path = Path('.env')
load_dotenv(dotenv_path=dotenv_path)

def run(input_path, analyse_path, sanitized_filename):
    logging.info('Flow Common : Starting')

    # Antivirus Analyse
    tool_clamav.run(input_path, analyse_path)

    # EVTX Analyse
    ## ZIRCOLITE
    tool_zircolite.zircolite_Windows(input_path, analyse_path)
    ## Requirement : import dashboard in ElasticSearch
    tool_elasticsearch.send_data_to_elk('send_data_to_elk', directory_path=f"{analyse_path}/zircolite", index_name="zircolite", elasticsearch_host=env["ES_HOST"], elasticsearch_user=env["ES_USER"], elasticsearch_password=env["ES_PASSWORD"])

    ## CHAINSAW
    tool_chainsaw.run(input_path, analyse_path)
    ## Requirement : import dashboard in ElasticSearch
    tool_elasticsearch.send_data_to_elk('send_data_to_elk', directory_path=f"{analyse_path}/chainsaw", index_name="chainsaw", elasticsearch_host=env["ES_HOST"], elasticsearch_user=env["ES_USER"], elasticsearch_password=env["ES_PASSWORD"])

    #tool_elasticsearch.add_index_pattern_to_kibana('add_index_pattern_to_kibana', kibana_host=env['KIBANA_HOST'], index_prefix='zircolite*', index_name='zircolite_test')

    ## Add timefield : matches.SystemTime / source : https://www.elastic.co/docs/api/doc/kibana/v8/operation/operation-createdataviewdefaultw#operation-createdataviewdefaultw-body-application-json-elastic-api-version-2023-10-31-data_view-timefieldname
