from config.default import *
from dotenv import load_dotenv
import os


load_dotenv(os.path.join(BASE_DIR, '.env'))


SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://{user}:{pw}@{url}:{port}/{db}'.format(
    user=os.getenv('DB_USER'),
    pw=os.getenv('DB_PASSWORD'),
    url=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT'),
    db=os.getenv('DB_NAME'))


SQLALCHEMY_TRACK_MODIFICATIONS = False


# SECRET_KEY = os.environ.get('SECRET_KEY')
SECRET_KEY = b'Zb3\x81\xdb\xf1\xd9\xd7-Knb\x8eB\xa5\x18'


ROOT_DIR = os.path.dirname(BASE_DIR)
STATIC_URL = '/static'
STATIC_DIR = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = [
    STATIC_DIR,
]
STATIC_ROOT = os.path.join(ROOT_DIR, '.static_root')
