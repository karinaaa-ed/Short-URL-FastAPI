import os
from dotenv import load_dotenv

load_dotenv()


DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_USER = os.getenv("SMTP_USER")

SECRET = os.getenv("SECRET_KEY")

DEFAULT_LINK_DAYS = os.getenv("DEFAULT_LINK_EXPIRE_DAYS")
DEFAULT_UNUSED_LINK_DAYS = os.getenv("DEFAULT_UNUSED_LINK_EXPIRE_DAYS")

MAX_ANONYMOUS_LINKS = os.getenv("MAX_ANONYMOUS_LINKS")
ANONYMOUS_LINK_EXPIRE_DAYS = os.getenv("ANONYMOUS_LINK_EXPIRE_DAYS")
