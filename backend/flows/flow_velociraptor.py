import logging
from prefect import flow
from tasks import *


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
    ## TODO --> sanitize evtx name
    tool_zircolite.zircolite_Windows(f'{output_path}/{sanitized_filename}.output', f'{output_path}/{sanitized_filename}.analyse')