import json
import os
from pathlib import Path
from typing import Callable, Dict

import boto3
import pytest
from moto import mock_s3, mock_secretsmanager, mock_sqs


def get_file_content(file: str, encoding: str = "utf-8") -> str:
    asset = Path(__file__).parent.resolve() / "assets" / file
    return asset.read_text(encoding=encoding)


@pytest.fixture(name="top_ten_movies")
def fixture_top_ten_movies() -> Dict:
    return json.loads(get_file_content("top_ten_movies.json"))


@pytest.fixture(name="top_movies")
def fixture_top_movies() -> Dict:
    return json.loads(get_file_content("250_movies.json"))


@pytest.fixture(name="omdb_movie_data")
def fixture_omdb_movie_data() -> Dict:
    return json.loads(get_file_content("omdb_movie_data.json"))


@pytest.fixture(name="sqs_incomming_payload")
def fixture_sqs_incomming_payload() -> Dict:
    return json.loads(get_file_content("sqs_incomming_payload.json"))


@pytest.fixture(name="list_of_enriched_movies")
def fixture_list_of_enriched_movies() -> Dict:
    return json.loads(get_file_content("list_of_enriched_movies.json"))


@pytest.fixture(name="base_movie_data")
def fixture_base_movie_data() -> Dict:
    return {
        "id": "tt0111161",
        "rank": "1",
        "title": "The Shawshank Redemption",
        "fullTitle": "The Shawshank Redemption (1994)",
        "year": "1994",
        "image": "https://m.media-amazon.com/images/M/MV5BMDFk.jpg",
        "crew": "Frank Darabont (dir.), Tim Robbins, Morgan Freeman",
        "imDbRating": "9.2",
        "imDbRatingCount": "2572473",
    }


@pytest.fixture(name="dummy_aws_credentials")
def fixture_dummy_aws_cretentials():
    os.environ["AWS_ACCESS_KEY_ID"] = "dummy"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "dummy"
    os.environ["AWS_SECURITY_TOKEN"] = "dummy"
    os.environ["AWS_SESSION_TOKEN"] = "dummy"


@pytest.fixture(name="mock_s3")
def fixture_s3_client(dummy_aws_credentials):
    with mock_s3():
        conn = boto3.client("s3", region_name="us-east-1")
        yield conn


@pytest.fixture(name="mock_sqs")
def fixture_sqs_client(dummy_aws_credentials):
    with mock_sqs():
        conn = boto3.client("sqs", region_name="us-east-1")
        yield conn


@pytest.fixture(name="mock_secretsmanager")
def fixture_secretsmanager_client(dummy_aws_credentials):
    with mock_secretsmanager():
        conn = boto3.client("secretsmanager", region_name="us-east-1")
        yield conn
