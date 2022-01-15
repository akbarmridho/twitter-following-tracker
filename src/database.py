from typing import Dict, List, TypedDict
from src import User, Config  # type: ignore
from mongoengine import connect as mongo_connect, Document, IntField, StringField, ListField, QuerySet  # type: ignore
from pymongo import MongoClient  # type: ignore


def connect(config: Config) -> MongoClient:
    return mongo_connect(config.MONGODB_DB_NAME, host=config.MONGODB_DB_HOST)


class UserPair(TypedDict):
    user: User
    document: Document


class Configuration(Document):
    key = StringField(required=True)
    value = StringField(required=True)


class Leaderboard(Document):
    username = StringField(required=True)


class UserDocument(Document):
    user_id = IntField(required=True)
    username = StringField(requried=True)
    name = StringField(default="")
    following = ListField(default=[])

    def to_dict(self) -> Dict:
        return {
            "user_id": self.user_id,
            "username": self.username,
            "name": self.name,
            "following": self.following
        }

    def to_user_class(self) -> User:
        return User.from_dict(self.to_dict())

    @classmethod
    def create_from_user_class(cls, user: User):
        """Create and save user document from twitter user class

        Args:
            user (User): User class

        Returns:
            User: Saved user document
        """
        return cls(**user.to_dict()).save()

    @staticmethod
    def users_from_query_set(users: QuerySet) -> List[UserPair]:
        """Convert user documents to list of User class

        Args:
            users (QuerySet): Users query set

        Returns:
            List[User]: List of twitter user
        """
        result: List[UserPair] = []

        for user in users:
            if isinstance(user, UserDocument):
                result.append({"user": user.to_user_class(), "document": user})

        return result

    @staticmethod
    def get_usernames(users: QuerySet) -> List[str]:
        """Convert user documents to list of usernames

        Args:
            users (QuerySet): Users query set

        Returns:
            List[str]: List of Twitter usernames
        """
        return [user.username for user in users]
