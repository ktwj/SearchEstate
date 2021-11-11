import os
#ローカルのみ
#CELERY_BROKER_URL = "redis://localhost:6379/1"
#CELERY_RESULT_BACKEND = "django-db"

#Herokuにデプロイするときはこっち
CELERY_BROKER_URL = os.environ.get("REDIS_URL")
CELERY_RESULT_BACKEND = os.environ.get("REDIS_URL")