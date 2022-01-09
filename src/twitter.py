from typing import Dict, List
from tweepy import Client  # type: ignore
from tweepy.client import Response  # type: ignore
from tweepy.errors import TooManyRequests  # type: ignore
from src import Config
from time import sleep
from random import randint
import logging


class User:
    user_id: int
    username: str
    name: str
    following: List = []
    changed = False

    def __init__(self, id: int, username: str, name: str, following: List = None):
        self.user_id = id
        self.username = username
        self.name = name

        if following is not None:
            self.following = following

    def get_following(self, client: Client):
        """Get list of user following. It's result will be saved in following property

        Args:
            client (Client): Tweepy API Client
        """
        self.following: List[User] = []
        current_client = client

        payload: Dict = {}

        while True:

            try:
                response: Response = current_client.get_users_following(
                    self.user_id, user_auth=True, max_results=999, **payload)

                twitter_users: List[Dict] = response.data

                for user in twitter_users:
                    self.following.append(
                        User(user["id"], user["username"], user["name"]))

                meta: Dict = response.meta

                if "next_token" in meta:
                    payload["pagination_token"] = meta["next_token"]
                else:
                    break

                sleep(randint(1, 3))

            except TooManyRequests:
                logging.warning(
                    'Request limit reached. Waiting for 20 minutes')
                sleep(20*60)
                current_client = Client(bearer_token=client.bearer_token, consumer_key=client.consumer_key,
                                        consumer_secret=client.consumer_secret, access_token=client.access_token, access_token_secret=client.access_token_secret)

    @property
    def following_usernames(self) -> List[str]:
        """List of user following usernames

        Returns:
            List[str]: List of username
        """
        return [user.username for user in self.following]

    def set_changed(self):
        """Set that user class data has changed
        """
        self.changed = True

    def set_unchanged(self):
        """Set unchanged
        """
        self.changed = False

    def to_dict(self) -> Dict:
        """Convert user class to dictionary

        Returns:
            Dict: Dictionary with user_id, username, name, and following as its keys
        """
        return {
            "user_id": self.user_id,
            "username": self.username,
            "name": self.name,
            "following": [user.to_dict() for user in self.following]
        }

    @classmethod
    def from_dict(cls, data: Dict):
        """Convert dictionary data to user class

        Args:
            data (Dict): User data

        Raises:
            Exception: Invalid data exception

        Returns:
            User: user class
        """
        if "user_id" not in data and "username" not in data and "name" not in data and "following" not in data:
            raise Exception('Invalid User data')

        return cls(data["user_id"], data["username"], data["name"], following=[cls.from_dict(user) for user in data["following"]])

    @classmethod
    def from_array(cls, users: List[Dict]):
        """Convert list of user dictionary into list of classes

        Args:
            users (List[Dict]): User list of dict

        Returns:
            List[User]: List of user
        """
        return [cls.from_dict(user) for user in users]

    @staticmethod
    def new_following(new: List[str], old: List[str]) -> List[str]:
        """Get new following username from two list

        Args:
            new (List[str]): List of new following usernames
            old (List[str]): List of old following usernames

        Returns:
            List[str]: usernames in new that are not in old
        """
        return list(set(new) - set(old))

    @staticmethod
    def new_unfollowing(new: List[str], old: List[str]) -> List[str]:
        """Get new unfollowing username from two list

        Args:
            new (List[str]): List of new following usernames
            old (List[str]): List of old following usernames

        Returns:
            List[str]: usernames in old that are not in new
        """
        return list(set(old) - set(new))


class API:
    client: Client
    config: Config

    def __init__(self, config: Config):
        self.config = config
        self.client = Client(config.TWITTER_BEARER_TOKEN, config.TWITTER_CUSTOMER_KEY,
                             config.TWITTER_CUSTOMER_SECRET, config.TWITTER_OAUTH_TOKEN, config.TWITTER_OAUTH_SECRET)

    def get_new_client(self) -> Client:
        config = self.config
        return Client(config.TWITTER_BEARER_TOKEN, config.TWITTER_CUSTOMER_KEY,
                      config.TWITTER_CUSTOMER_SECRET, config.TWITTER_OAUTH_TOKEN, config.TWITTER_OAUTH_SECRET)

    def get_users(self, users: List[str]) -> List[User]:
        """Get twitter user ids by username

        Args:
            users (List[str]): List of twitter username
        """
        response: Response = self.client.get_users(usernames=users)

        twitter_users: List[Dict] = response.data

        result: List[User] = []

        for user in twitter_users:
            result.append(User(user["id"], user["username"], user["name"]))

        return result

    def get_metrics(self, users: List[str]) -> Dict[str, Dict]:
        """Get users description and followers count

        Args:
            users (List[str]): [description]

        Returns:
            Dict: [description]
        """
        response = self.client.get_users(
            usernames=users, user_auth=True, user_fields=['public_metrics', 'description', 'created_at', "entities"])
        result: List[Dict] = response.data

        metrics = {}

        for user in result:
            urls = []

            if "url" in user["entities"] and "urls" in user["entities"]["url"]:
                for url in user["entities"]["url"]["urls"]:
                    urls.append(url["display_url"])

            if "description" in user["entities"] and "urls" in user["entities"]["description"]:
                for url in user["entities"]["description"]["urls"]:
                    urls.append(url["display_url"])

            metrics[user["username"]] = {"description": user["description"],
                                         'followers_count': user["public_metrics"]["followers_count"],
                                         'created_at': user["created_at"],
                                         "urls": urls
                                         }

        return metrics
