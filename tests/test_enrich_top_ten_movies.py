import os

import pytest
from requests import HTTPError

from cat_in_the_movies.enrich_top_ten_movies import (
    enrich_movie_with_data_from_omdb,
    get_movies_from_records,
    get_omdb_api_key,
    get_the_movie_details_from_omdbapi,
    process_movies,
    save_to_bucket,
)


def test_save_to_bucket(list_of_enriched_movies, mock_s3):
    bucket = "dummy_bucket"
    os.environ["BUCKET_NAME"] = bucket
    mock_s3.create_bucket(Bucket=bucket)
    result = save_to_bucket(list_of_movies=list_of_enriched_movies)
    assert result["ResponseMetadata"]["HTTPStatusCode"] == 200


def test_get_omdb_api_key(mock_secretsmanager):
    secret_name = "dummy-secret"
    secret_value = "batman_is_bruce_wayne"
    os.environ["OMDB_SECRET_NAME"] = secret_name
    mock_secretsmanager.create_secret(Name=secret_name, SecretString=secret_value)
    assert get_omdb_api_key() == secret_value


def test_get_the_movie_details_from_omdbapi_ok(requests_mock):
    dummy_url = "https://test"
    api_key = "123456"
    imdb_id = "tt55"
    os.environ["OMDB_API_URL"] = dummy_url
    response = {"test": "OK"}
    requests_mock.get(f"{dummy_url}/?apikey={api_key}&i={imdb_id}", json=response)
    assert (
        get_the_movie_details_from_omdbapi(imdb_id=imdb_id, api_key=api_key) == response
    )


def test_get_the_movie_details_from_omdbapi_raises_404(requests_mock):
    dummy_url = "https://test"
    api_key = "123456"
    imdb_id = "tt55"
    os.environ["OMDB_API_URL"] = dummy_url
    requests_mock.get(f"{dummy_url}/?apikey={api_key}&i={imdb_id}", status_code=404)
    with pytest.raises(HTTPError):
        get_the_movie_details_from_omdbapi(imdb_id=imdb_id, api_key=api_key)


def test_enrich_movie_with_data_from_omdb(base_movie_data, omdb_movie_data):
    result = enrich_movie_with_data_from_omdb(
        base_movie_data=base_movie_data, omdb_movie_data=omdb_movie_data
    )
    assert result["omdb_data"] == omdb_movie_data


def test_get_movies_from_records(sqs_incomming_payload):
    records = sqs_incomming_payload["Records"]
    movies = get_movies_from_records(records=records)
    assert next(movies)["title"] == "The Shawshank Redemption"


def test_process_movies(sqs_incomming_payload, mocker):
    records = sqs_incomming_payload["Records"]
    movies = get_movies_from_records(records=records)
    mocker.patch(
        "cat_in_the_movies.enrich_top_ten_movies.get_omdb_api_key", return_value="test"
    )
    mocker.patch(
        "cat_in_the_movies.enrich_top_ten_movies.get_the_movie_details_from_omdbapi",
        return_value="test",
    )
    mocker.patch(
        "cat_in_the_movies.enrich_top_ten_movies.enrich_movie_with_data_from_omdb",
        return_value="Batman",
    )
    assert process_movies(movies=movies) == ["Batman"]
