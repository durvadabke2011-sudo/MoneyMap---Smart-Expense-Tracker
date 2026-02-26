import os

DB_HOST     = os.environ.get("DB_HOST", "switchyard.proxy.rlwy.net")
DB_PORT     = int(os.environ.get("DB_PORT", 39650))
DB_USER     = os.environ.get("DB_USER", "root")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "SJcAmhIgmnJUJCEJpOMuskAUQDULGUic")
DB_NAME     = os.environ.get("DB_NAME", "railway")

SECRET_KEY  = os.environ.get("SECRET_KEY", "moneymap_super_secret_2024")