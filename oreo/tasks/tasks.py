import re
import hashlib
import logging

from celery import shared_task
from . import *             # Need to declare all python scripts in __init__.py


@shared_task(bind=True, name='task_extract_files')
def task_extract_files(self, filepath, output_filepath, password):
    logging.info(f'Task Extract files : Call task')
    run_extract.run(filepath, output_filepath, password, nested=False)


@shared_task(bind=True, name='task_sha256')
def task_sha256(self, filepath:str):
    logging.info(f'Task SHA256 : Call task')
    run_sha256.sha256_generate(filepath)
    


