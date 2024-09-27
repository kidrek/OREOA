import argparse, logging, os

## Load variables from .env file
from dotenv import load_dotenv
from pathlib import Path
from os import environ as env
dotenv_path = Path('.env')
load_dotenv(dotenv_path=dotenv_path)


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

    if input_evidence and output_analyse:
        # Load all prefect modules
        from prefect import flow
        from backend.tasks import *
        from backend.flows import *

        ## Start - Processing Data
        flow_common.run(input_evidence, output_analyse)
    else:
        parser.print_help()
        