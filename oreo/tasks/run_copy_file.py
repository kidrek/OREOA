import io, logging, os, re, subprocess, zipfile

def run(filepath:str, output_filepath:str):
    logging.info("Copy task...", 60)

    command = [
        'cp', '-rf',
        filepath, 
        output_filepath
    ]        

    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"output: {result.stdout}")
        if result.stderr:
            print(f"error: {result.stderr}")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")
        raise e
