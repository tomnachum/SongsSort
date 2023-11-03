import os
from dotenv import load_dotenv
from schemas.env_vars import EnvVars


def get_env_vars() -> EnvVars:
    load_dotenv()
    return EnvVars(**os.environ)
