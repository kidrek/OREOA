import io, logging, os, re, subprocess, time, zipfile

def run(filepath:str, output_filepath:str, password:str='', nested:bool=True):
    logging.info(f'Task Extract files : Running task')

    """ Extract a zip file including any nested zip files
        Delete the zip file(s) after extraction
    """
    logging.info(f'Task Extract files : Extract file {filepath}')
    with zipfile.ZipFile(filepath, 'r') as zfile:
        if nested == False:
            command = [
                '7z', 'x', '-y', '-r', f"-p{password}",
                filepath, 
                f'-o{output_filepath}'
            ]        
        else:
            command = [
                '7z', 'x', '-y', '-r',
                filepath, 
                f'-o{output_filepath}'
            ]

        try:
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            if nested:
                os.remove(filepath)
                time.sleep(0.01)      

            print(f"output: {result.stdout}")
            if result.stderr:
                print(f"error: {result.stderr}")
        except subprocess.CalledProcessError as e:
            print(f"Error: {e.stderr}")
            raise e
        

    for root, dirs, files in os.walk(output_filepath):
        for filename in files:
            if re.search(r'\.zip$', filename):
                fileSpec = os.path.join(root, filename)
                run(fileSpec, output_filepath, nested=True)