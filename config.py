import os

DB_HOST     = os.environ.get("DB_HOST", "localhost")
DB_USER     = os.environ.get("DB_USER", "moneymap_user")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "moneymap123")
DB_NAME     = os.environ.get("DB_NAME", "moneymap")

SECRET_KEY  = os.environ.get("SECRET_KEY", "moneymap_super_secret_2024")