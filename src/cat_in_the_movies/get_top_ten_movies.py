import json
from typing import List

import boto3
import requests

from cat_in_the_movies.logger import LOGGER
from cat_in_the_movies.utils import get_env_var


def fetch_movies() -> List:
    LOGGER.info("Getting top 250 movies")
    url = get_env_var("TOP_MOVIES_URL")
    LOGGER.debug("Using url '%s'", url)
    response = requests.get(url)
    response.raise_for_status()
    return response.json()["items"]


def get_top_ten_movies(movies: List) -> List:
    sorted_top_250_movies = sorted(movies, key=lambda movie: int(movie["rank"]))
    top_ten_movies = sorted_top_250_movies[:10]
    return top_ten_movies


def send_message(message_body: List):
    LOGGER.info("Sending message to AWS SQS")
    region = get_env_var("AWS_REGION")
    queue_url = get_env_var("SQS_QUEUE_URL")
    LOGGER.debug("Using region '%s' and queue url '%s'", region, queue_url)
    sqs = boto3.client("sqs", region_name=region)
    message = json.dumps(message_body)
    response = sqs.send_message(QueueUrl=queue_url, MessageBody=message)
    LOGGER.debug("Response from SQS '%s'", response)
    return response


def event_handler(_event, _context):
    LOGGER.info("Starting the app")
    movies = fetch_movies()
    top_ten_movies = get_top_ten_movies(movies=movies)
    send_message(message_body=top_ten_movies)
    LOGGER.info("Finished sucessfully")
