from typing import Dict, List, TypedDict
from src.config import Config
from datetime import datetime
from urllib.parse import quote
from time import sleep
import requests


class AirtableData(TypedDict):
    tracked_user: str
    followed_user: str
    followed_at: datetime
    created_at: datetime
    followers_count: int
    description: str


def convert(source: AirtableData) -> Dict:
    return {
        "fields": {
            "Tracked User": source["tracked_user"],
            "Followed User": source["followed_user"],
            "Followed At": source["followed_at"].strftime('%Y-%m-%d'),
            "Created At": source["created_at"].strftime('%Y-%m-%d'),
            "Account Url": f'https://twitter.com/{source["followed_user"]}',
            "Follower Count": source["followers_count"],
            "Description": source["description"]
        }
    }


class Airtable:
    config: Config
    base_url: str
    token: str

    def __init__(self, config: Config):
        self.config = config
        self.base_url = f'https://api.airtable.com/v0/{config.AIRTABLE_APP_ID}/{quote(config.AIRTABLE_TABLE_NAME)}'
        self.token = config.AIRTABLE_API_KEY

    def save(self, data: List[AirtableData]):
        """Save new list of data to airtable

        Args:
            data (List[AirtableData]): [description]

        Raises:
            Exception: [description]
        """
        for chunk in [data[i:i + 10] for i in range(0, len(data), 10)]:
            response = requests.post(self.base_url, json={"records": [
                convert(datum) for datum in chunk]}, headers={'Authorization': f'Bearer {self.token}'})
            if not response.ok:
                raise Exception(response.text)
            sleep(0.5)
