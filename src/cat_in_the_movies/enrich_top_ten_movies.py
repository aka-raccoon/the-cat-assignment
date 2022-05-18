import json
from datetime import datetime
from typing import Dict, Generator, List

import boto3
import requests

from cat_in_the_movies.logger import LOGGER
from cat_in_the_movies.utils import get_env_var


def save_to_bucket(list_of_movies: List, filename: str = "top_10_movies.json") -> Dict:
    LOGGER.info("Saving list of movies to S3 bucket")
    s3_client = boto3.client("s3")
    bucket_name = get_env_var("BUCKET_NAME")
    now = datetime.now()
    file = json.dumps(list_of_movies, indent=4)
    reply = s3_client.put_object(
        Body=file, Bucket=bucket_name, Key=f"{now:%Y/%m/%d}/{filename}"
    )
    LOGGER.debug("S3 reply: %s", reply)
    return reply


def get_omdb_api_key() -> str:
    LOGGER.debug("Fetching OMDB API KEY from AWS secret manager")
    secret_manager = boto3.client("secretsmanager")
    secret_name = get_env_var("OMDB_SECRET_NAME")
    response = secret_manager.get_secret_value(SecretId=secret_name)
    return response["SecretString"]


def get_the_movie_details_from_omdbapi(imdb_id: str, api_key: str) -> Dict:
    params = {"apikey": api_key, "i": imdb_id}
    url = get_env_var("OMDB_API_URL")
    response = requests.get(url=url, params=params)
    response.raise_for_status()
    return response.json()


def enrich_movie_with_data_from_omdb(
    base_movie_data: Dict, omdb_movie_data: Dict
) -> Dict:
    base_movie_data["omdb_data"] = omdb_movie_data
    return base_movie_data


def get_movies_from_records(records: List[Dict]) -> Generator[Dict, None, None]:
    LOGGER.debug("Records from SQS: %s", records)
    return (movie for record in records for movie in json.loads(record["body"]))


def process_movies(movies: Generator[Dict, None, None]) -> List:
    list_of_enriched_movies = []
    api_key = get_omdb_api_key()
    for movie in movies:
        LOGGER.info("Processing movie %s", movie["title"])
        omdb_details = get_the_movie_details_from_omdbapi(
            imdb_id=movie["id"], api_key=api_key
        )
        enriched_movie_data = enrich_movie_with_data_from_omdb(
            base_movie_data=movie, omdb_movie_data=omdb_details
        )
        list_of_enriched_movies.append(enriched_movie_data)
    LOGGER.debug("List of processed movies %s", list_of_enriched_movies)
    return list_of_enriched_movies


def event_handler(event, _context):
    LOGGER.info("Starting the app")
    movies = get_movies_from_records(records=event["Records"])
    enriched_movies = process_movies(movies=movies)
    save_to_bucket(enriched_movies)
    LOGGER.info("Finished sucessfully")
