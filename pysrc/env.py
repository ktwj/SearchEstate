import os
from dotenv import load_dotenv
load_dotenv()

APP_database = os.environ['APP_database']
APP_user = os.environ['APP_user']
APP_password = os.environ['APP_password']
APP_host = os.environ['APP_host']
APP_port = os.environ['APP_port']
APP_secret_key = os.environ['APP_secret_key']