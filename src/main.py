from typing import Dict, List
from mongoengine.queryset.queryset import QuerySet
from src import User, Telegram, Config, UserDocument, UserPair, TwitterAPI, Sheets
from datetime import date
import logging


def format_message(user: str, following_changes: List[str]) -> str:
    today = date.today().strftime('%m/%d/%Y')

    messages = ['@{} start following @{} on {}'.format(
        user, following, today) for following in following_changes]

    message = '\n'.join(messages)

    return (message[:4090] + '...') if len(message) > 4087 else message


class App:

    twitter_api: TwitterAPI
    telegram: Telegram
    spreadsheet: Sheets
    config: Config
    users: List[UserPair] = []

    def __init__(self, config: Config):
        self.config = config
        self.twitter_api = TwitterAPI(config)
        self.telegram = Telegram(config)
        self.spreadsheet = Sheets(config)

    def _initialize(self):
        """Initialize the application setup
        """
        to_sync = self._get_to_sync_users(
            self.config.WATCHED_USERS, UserDocument.get_usernames(UserDocument.objects))

        self._delete_users(to_sync["to_delete"])
        self._add_users(to_sync["to_add"])

        self.users.extend(
            UserDocument.users_from_query_set(UserDocument.objects))

        self.telegram.initialize()

    def _get_to_sync_users(self, new: List[str], old: List[str]) -> Dict:
        """Compare old and new username list

        Args:
            new (List[str]): new username list
            old (List[str]): old username list

        Returns:
            Dict: dict with to_delete and to_add keys
        """
        new_set = set(new)
        old_set = set(old)

        return {
            "to_delete": list(old_set-new_set),
            "to_add": list(new_set-old_set)
        }

    def _delete_users(self, usernames: List[str]):
        """Delete user from database

        Args:
            usernames (List[str]): [description]
        """
        if len(usernames) == 0:
            return

        users: QuerySet = UserDocument.objects(username__in=usernames)
        users.delete()

    def _add_users(self, usernames: List[str]):
        """Add user from database

        Args:
            usernames (List[str]): [description]
        """
        if len(usernames) == 0:
            return

        users: List[User] = self.twitter_api.get_users(usernames)

        for user in users:
            user.get_following(self.twitter_api.client)
            UserDocument.create_from_user_class(user)

    def _notify_new_following(self, user: User, usernames: List[str]):
        if len(usernames) == 0:
            return

        message = format_message(user.username, usernames)

        logging.info(message)

        self.telegram.send_message(message)
        self.spreadsheet.append([[f'@{user.username}', f'@{username}',
                                date.today().strftime('%m/%d/%Y')] for username in usernames])

    def _notify_new_unfollowing(self, user: User, usernames: List[str]):
        if len(usernames) == 0:
            return
        pass

    def _save_database(self):
        """Persist following data to user
        """
        for user in self.users:
            if user["user"].changed:
                user["document"].following = [user.to_dict()
                                              for user in user["user"].following]
                user["user"].set_unchanged()
                user["document"].save()

    def sync(self):
        """Monitor new following and unfollowing then notify to user
        """
        for pair in self.users:
            user = pair["user"]
            old = user.following_usernames.copy()
            user.get_following(self.twitter_api.client)
            new = user.following_usernames.copy()

            new_following = User.new_following(new, old)
            new_unfollowing = User.new_unfollowing(new, old)

            if len(new_following) != 0 or len(new_unfollowing) != 0:
                user.set_changed()
                self._notify_new_following(user, new_following)
                self._notify_new_unfollowing(user, new_unfollowing)

        self._save_database()
