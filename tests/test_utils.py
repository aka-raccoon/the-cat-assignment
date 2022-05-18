import os

import pytest

from cat_in_the_movies.exceptions import RequiredEnvironmentVariableMissing
from cat_in_the_movies.utils import get_env_var


def test_get_env_var_ok():
    os.environ["BRUCE"] = "wayne"
    assert get_env_var(name="BRUCE") == "wayne"


def test_get_env_var_raises():
    pikachu = "pikachu"
    if os.getenv(pikachu) is not None:
        del os.environ[pikachu]
    with pytest.raises(RequiredEnvironmentVariableMissing):
        assert get_env_var(name=pikachu)
