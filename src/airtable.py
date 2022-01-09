from typing import Callable, Dict, List, TypedDict, Union
from src.config import Config
from datetime import datetime
from urllib.parse import quote
from time import sleep
import requests  # type: ignore


class NewFollowing(TypedDict):
    tracked_user: str
    tracked_user_points: int
    followed_user: str
    followed_at: datetime
    created_at: datetime
    created_at_points: int
    followers_count: int
    followers_count_points: int
    description: str
    description_points: int
    urls: List[str]
    url_points: int


def convert_raw_data(source: NewFollowing) -> Dict:
    return {
        "fields": {
            "Username": source["followed_user"],
            "Followed At": source["followed_at"].strftime('%Y-%m-%d'),
            "Account Url": f'https://twitter.com/{source["followed_user"]}',
            "Description": source["description"],
            "Description Points": source["description_points"],
            "Followed By": source["tracked_user"],
            "Followed By Points": source["tracked_user_points"],
            "Created At": source["created_at"].strftime('%Y-%m-%d'),
            "Created At Points": source["created_at_points"],
            "Followers Count": source["followers_count"],
            "Followers Count Points": source["followers_count_points"],
            "Links": "\n".join(source["urls"]),
            "Links Points": source["url_points"],
            "Score": source["url_points"]+source["followers_count_points"]+source["created_at_points"]+source["tracked_user_points"]+source["description_points"]
        }
    }


def convert_new_following(source: NewFollowing) -> Dict:
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


def convert_leaderboard(source: NewFollowing) -> Dict:
    return {
        "fields": {
            "Username": source["followed_user"],
            "Description": source["description"],
            "Score": source["url_points"]+source["followers_count_points"]+source["created_at_points"]+source["tracked_user_points"]+source["description_points"],
            "Created At": source["created_at"].strftime('%Y-%m-%d'),
            "Account Url": f'https://twitter.com/{source["followed_user"]}',
            "Links": "\n".join(source["urls"])
        }
    }


class Airtable:
    config: Config
    base_url: str
    token: str

    def __init__(self, config: Config):
        self.config = config
        self.base_url = f'https://api.airtable.com/v0/{config.AIRTABLE_APP_ID}'
        self.token = config.AIRTABLE_API_KEY

    def _get_table_content(self, table: str) -> List[Dict]:
        result: List[Dict[str, Dict]] = []
        next_token = ''

        while True:

            if next_token == '':
                response = requests.get(f"{self.base_url}/{quote(table)}",
                                        headers={'Authorization': f'Bearer {self.token}'})
            else:
                response = requests.get(f"{self.base_url}/{quote(table)}",
                                        headers={
                                            'Authorization': f'Bearer {self.token}'},
                                        params={"offset": next_token}
                                        )

                sleep(0.5)

            if not response.ok:
                raise Exception(response.text)

            response_payload = response.json()

            result.extend(response_payload["records"])

            if "offset" in response_payload:
                next_token = response_payload["offset"]
            else:
                break

        return [row["fields"] for row in result if len(row["fields"].keys()) != 0]

    def _add_rows(self, table: str, data: List[NewFollowing], converter: Callable[[NewFollowing], Dict]):
        """Save new list of data to airtable

        Args:
            data (List[Dict]): [description]

        Raises:
            Exception: [description]
        """
        for chunk in [data[i:i + 10] for i in range(0, len(data), 10)]:
            response = requests.post(f"{self.base_url}/{quote(table)}", json={"records": [
                converter(datum) for datum in chunk]}, headers={'Authorization': f'Bearer {self.token}'})
            if not response.ok:
                raise Exception(response.text)
            sleep(0.5)

    def get_tracked_users(self):
        return self._get_table_content(self.config.AIRTABLE_TABLE_TRACKED_USERS)

    def get_keywords(self):
        return self._get_table_content(self.config.AIRTABLE_TABLE_KEYWORDS)

    def save(self, data: List[NewFollowing]):
        self._add_rows(self.config.AIRTABLE_TABLE_RESULT,
                       data, convert_raw_data)
        self._add_rows(self.config.AIRTABLE_TABLE_LEADERBOARD,
                       data, convert_leaderboard)
