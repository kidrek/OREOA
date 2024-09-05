from prefect import task
import hashlib, logging, os, re, shlex, subprocess
## Load variables from .env file
from os import environ as env

@task(log_prints=True)
def determine_evidence_type(filename):
    # Determine evidence type
    if re.match(env['VELOCIRAPTOR_EVIDENCE_PATTERN'], filename, re.IGNORECASE):
        evidence_type = "velociraptor"
        print("Velociraptor evidence")
    else:
        evidence_type = "other"    
    return evidence_type

@task(log_prints=True)
def unpack(input_filepath:str, output_filepath:str, password:str='', specific_file: str='', extraction_absolute_path:bool=True):
    logging.info(f'Task unpack archive : Running task')

    """ Extract a zip file including any nested zip files
        Delete the zip file(s) after extraction
    """
    logging.info(f'Task unpack archive : Extract file {input_filepath}')

    cmd_options = " -y -r "
    if len(password) > 0: cmd_options = cmd_options + f'-p\'{password}\' '
    if len(specific_file) > 0: cmd_options = cmd_options + f'\'-i!{specific_file}\' '

    cmd_switch = ''
    if extraction_absolute_path == True: 
        cmd_switch = ' x ' 
    else: 
        cmd_switch = ' e '

    command = (
        f"7z "
        f"{cmd_switch}"
        f"{cmd_options} "
        f"{input_filepath} "
        f"-o{output_filepath} "
    )

    try:
        #logging.info(command)
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        logging.info(f"output: {result.stdout}")
        if result.stderr:
            logging.error(f"error: {result.stderr}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error: {e.stderr}")



@task(log_prints=True)
def generate_hash(hash:str="sha256", filepath:str=None):
    logging.info(f'Task generate hash : Starting')

    # Set algorithm
    hash = hash.lower()
    if hash == "sha256":
        hash_algo = hashlib.sha256()
    elif hash == "sha1":
        hash_algo = hashlib.sha1()
    elif hash == "md5":
        hash_algo = hashlib.md5()

    try:
        with open(filepath,"rb") as f:
            # Read and update hash string value in blocks of 4K
            for byte_block in iter(lambda: f.read(4096),b""):
                hash_algo.update(byte_block)
            with open(f"{filepath}.{hash}","w") as f:
                f.write(hash_algo.hexdigest())
            logging.info(f"Task generate hash : Filepath: {filepath} / {hash}: {hash_algo.hexdigest()}")
    except FileNotFoundError:
        logging.error(f'Task generate hash : File not found: {filepath}')

@task(log_prints=True)
def move_file(filepath:str, output_filepath:str):
    logging.info(f'Task move file : starting')

    command = [
        'mv', '-f',
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

@task(log_prints=True)
def copy_file(filepath:str, output_filepath:str):
    logging.info(f'Task copy file : starting')

    command = [
        'cp', '-f',
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

@task(log_prints=True)
# Function to replace all characters, except 'a-zA-Z0-9._-' by -
def sanitize_file_name(input_filename):
    sanitized_name = re.sub(r'[^a-zA-Z0-9._-]', '-', input_filename).lower()
    return sanitized_name


@task(log_prints=True)
def find_files(pattern, search_path):
      fdfind_command = [
         'fdfind', 
         '-a', 
         '-i', 
         '-e', pattern,
         '--full-path', search_path,
         '-x', 'dirname', '{}'
      ]

      try: 
         result = (subprocess.check_output(
            shlex.join(fdfind_command) + ' | ' +
            shlex.join(['sort', '-n']) + '|' +
            shlex.join(['uniq']),
            shell=True
         ).decode('utf-8'))
      except subprocess.CalledProcessError as e:
         print(f"Error: {e.stderr}")
         raise e
      
      directories = []
      for dir in result.split('\n'):
         if len(dir) > 0:
            directories.append(dir)
      return directories

