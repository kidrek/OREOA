import logging
from backend.tasks import utility

def run(input_path:str, output_path, sanitized_filename, password):
    logging.info('Flow Velociraptor : Starting')

    # Decompress archive
    utility.unpack(input_filepath = f"{input_path}", output_filepath = f"{output_path}", specific_file='data.zip', password = password, extraction_absolute_path=False)
    utility.unpack(input_filepath = f"{output_path}/data.zip", output_filepath = f"{output_path}/", extraction_absolute_path=True)
