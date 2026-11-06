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
        api_token = self.dict.get(key)
        if not api_token:
            raise ValueError(f"No '{key}' key found. Check your .env file ({self.path}).")
        return api_token
