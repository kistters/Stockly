import os
from dotenv import load_dotenv

load_dotenv()


def get_env(env_key: str) -> any:
    try:
        return os.environ[env_key]
    except KeyError as e:
        raise ValueError(f"No {env_key} found. Please set the {env_key} environment variable in the .env file.")
