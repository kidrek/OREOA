import argparse, logging, os
from prefect import flow, task
from prefect_dask.task_runners import DaskTaskRunner
from backend.tasks import *

## Load variables from .env file
from dotenv import load_dotenv
from pathlib import Path
from os import environ as env
dotenv_path = Path('backend/.env')
load_dotenv(dotenv_path=dotenv_path)



@flow(task_runner=DaskTaskRunner(cluster_kwargs={"processes": False}))
def investigation_flow(input_evidence, output_analyse):

    ## Analyse Antivirale
    tool_clamav.run.submit(input_evidence, output_analyse)
    
    ## Analyse EVTX
    tool_zircolite.run2Timesketch.submit(input_evidence, output_analyse)
    tool_chainsaw.run.submit(input_evidence, output_analyse)

    ## SuperTimeline
    tool_plaso.run_log2timeline.submit(input_evidence, output_analyse)



if __name__=="__main__":
    logging.info(f"Running daemon")

    parser = argparse.ArgumentParser(
                    prog='OREOA',
                    description='Tool to process and analyse forensic data')

    parser.add_argument('-i', '--input_evidence')
    parser.add_argument('-o', '--output_analyse')
    args = parser.parse_args()

    input_evidence = args.input_evidence
    output_analyse = args.output_analyse

    ## Start - Processing Data
    os.makedirs(f"{output_analyse}", exist_ok=True)
    investigation_flow(input_evidence, output_analyse)

    tool_plaso.run_psort2json(f"{output_analyse}/plaso/plaso_log2timeline.plaso", output_analyse)


    ## Start - Sending results to ElasticSearch
    if len(env['ES_HOST']) > 0:
        for module in ['chainsaw','plaso', 'zircolite']:
            tool_elasticsearch.send_data_to_elk('send_data_to_elk', directory_path=f"{output_analyse}/{module}", index_name=module, elasticsearch_host=env["ES_HOST"], elasticsearch_user=env["ES_USER"], elasticsearch_password=env["ES_PASSWORD"])