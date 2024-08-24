import hashlib, logging, re, subprocess, time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path

from oreo.celery import app
from celery import chain


from dotenv import load_dotenv
from os import environ as env

## Load variables from .env file
dotenv_path = Path('.env')
load_dotenv(dotenv_path=dotenv_path)


class MyHandler(FileSystemEventHandler):
    def on_created(self, event):
        print(f'File {event.src_path} has been created')
        app.send_task('task_init', args=(event.src_path,), retry=True)


if __name__ == "__main__":
    logging.info(f"Running daemon")

    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path=env['ARTIFACT_PATH'], recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()



