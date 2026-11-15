import os

import dotenv


class EnvConfig:
    def __init__(self, path: str | None = None) -> None:
        self.path = path
        if self.path:
            self.dotenv_file = dotenv.find_dotenv(self.path)
        else:
            self.dotenv_file = dotenv.find_dotenv()
        self.dict = dotenv.dotenv_values(self.dotenv_file)

    def get(self, key: str):
        value = self.dict.get(key) or os.environ.get(key)
        if not value:
            raise ValueError(f"No '{key}' key found. Check your .env file ({self.path}).")
        return value
