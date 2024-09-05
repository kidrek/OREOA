import logging
from backend.tasks import *

# Load flow from prefect
from prefect import flow
from prefect_dask.task_runners import DaskTaskRunner

@flow(task_runner=DaskTaskRunner(cluster_kwargs={"processes": False}))
def investigate(input_evidence, output_analyse):
    logging.info('Flow investigation one device : Starting')

    ## SuperTimeline
    tool_plaso.run_log2timeline.submit(input_evidence, output_analyse)
