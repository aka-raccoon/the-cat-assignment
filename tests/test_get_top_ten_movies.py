import os

import pytest
from requests import HTTPError

from cat_in_the_movies.get_top_ten_movies import (
    fetch_movies,
    get_top_ten_movies,
    send_message,
)


def test_fetch_movies_ok(requests_mock):
    movies_url = "https://dummy_url"
    os.environ["TOP_MOVIES_URL"] = movies_url
    response = {"items": {"test": "OK"}}
    requests_mock.get(movies_url, json=response)
    assert fetch_movies() == response["items"]


def test_fetch_movies_raises_404(requests_mock):
    movies_url = "https://dummy_url"
    os.environ["TOP_MOVIES_URL"] = movies_url
    requests_mock.get(movies_url, status_code=404)
    with pytest.raises(HTTPError):
        fetch_movies()


def test_get_top_ten_movies(top_movies):
    movies = top_movies["items"]
    top_ten_sorted_movies = get_top_ten_movies(movies=movies)
    assert top_ten_sorted_movies[2]["rank"] == "3"
    assert top_ten_sorted_movies[8]["rank"] == "9"


def test_send_message(mock_sqs):
    os.environ["AWS_REGION"] = "us-east-1"
    os.environ["SQS_QUEUE_URL"] = "test"
    mock_sqs.create_queue(QueueName="test")
    response = send_message([{"test": "ok"}])
    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
