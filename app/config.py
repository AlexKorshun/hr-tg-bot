import os
from dotenv import load_dotenv

def load_config():
    local_env = os.path.join(os.getcwd(), '.env.local')
    default_env = os.path.join(os.getcwd(), '.env')

    if os.path.exists(local_env):
        load_dotenv(dotenv_path=local_env, override=True)
        print("Loaded configuration from .env.local")
    elif os.path.exists(default_env):
        load_dotenv(dotenv_path=default_env, override=True)
        print("Loaded configuration from .env")
    else:
        raise FileNotFoundError(
            "Configuration file not found: neither .env.local nor .env exists."
        )

load_config()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
ROOT_ADMIN_ID = os.getenv("ROOT_ADMIN_ID").split(',')

if not BOT_TOKEN or not DATABASE_URL:
    raise RuntimeError("Required environment variables are missing")
