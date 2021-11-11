from flask import Flask
from pysrc.celery_maker import make_celery
import settings

app = Flask(__name__)

app.config.update(
    CELERY_BROKER_URL=settings.CELERY_BROKER_URL,
    CELERY_RESULT_BACKEND=settings.CELERY_RESULT_BACKEND
)
celery = make_celery(app)