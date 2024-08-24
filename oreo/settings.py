

INSTALLED_APPS = [
    'oreo.tasks',  # Enregistrement des tasks présentes dans le path oreo/tasks
]

REDIS_BASE_URL="redis://127.0.0.1:6379"
CELERY_BROKER_URL = f'{REDIS_BASE_URL}/0'
CELERY_RESULT_BACKEND = f'{REDIS_BASE_URL}/1'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
CELERY_WORKER_CONCURRENCY=1
#CELERY_TIMEZONE = 'Asia/Almaty'
#CELERY_BEAT_SCHEDULE = {
#    "amount-counting": {
#        "task": "profile.tasks.amount_counting",
#        "schedule": 60.0,
#    },
#}
