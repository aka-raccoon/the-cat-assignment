class CatInTheMoviesException(Exception):
    pass


class RequiredEnvironmentVariableMissing(CatInTheMoviesException):
    def __init__(self, name: str):
        self.name = name
        super().__init__(f"Environment variable '{self.name}' is required.")
