import os

from cat_in_the_movies.exceptions import RequiredEnvironmentVariableMissing


def get_env_var(name: str) -> str:
    try:
        return os.environ[name]
    except KeyError as error:
        raise RequiredEnvironmentVariableMissing(name=name) from error
