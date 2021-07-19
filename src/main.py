from typing import Dict, List, TypedDict
from mongoengine.queryset.queryset import QuerySet
from src import User, Telegram, Config, UserDocument, UserPair, TwitterAPI, Sheets, Configuration
from datetime import date
from random import sample
import logging


def format_message(user: str, following_changes: List[str]) -> str:
    today = date.today().strftime('%m/%d/%Y')

    messages = ['@{} start following @{} on {}'.format(
        user, following, today) for following in following_changes]

    message = '\n'.join(messages)

    return (message[:4090] + '...') if len(message) > 4087 else message


class Progress(TypedDict):
    list: List[str]
    users: List[UserPair]


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

    def _get_check_progress(self) -> List[str]:
        progress: QuerySet = Configuration.objects(key="PROGRESS")
        if progress.count() == 0:
            Configuration(key="PROGRESS", value="").save()
            return []
        elif progress.count() == 1:
            value: str = progress.first().value
            if value == "":
                return []
            return value.split(',')
        else:
            raise Exception('Cannot get progress')

    def _get_user_pair_from_list(self, usernames: List[str]) -> List[UserPair]:
        result: List[UserPair] = []

        for user in usernames:
            user_document: UserDocument = UserDocument.objects(
                username=user).first()

            result.append(
                UserPair(user=user_document.to_user_class(), document=user_document))

        return result

    def _add_usernames_to_saved_progress(self, usernames: List[str]):
        old_progress = self._get_check_progress()
        old_progress.extend(usernames)

        progress: Configuration = Configuration.objects(key="PROGRESS").first()
        progress.value = ','.join(old_progress)
        progress.save()

    def _get_users_to_check(self) -> Progress:
        usernames = UserDocument.get_usernames(UserDocument.objects)
        progress = self._get_check_progress()

        to_check = list(set(usernames) - set(progress))

        if len(to_check) == 0:
            document: Configuration = Configuration.objects(
                key='PROGRESS').first()
            document.value = ""
            document.save()

            if len(usernames) < self.config.SYNC_COUNT:
                return Progress(list=usernames, users=self._get_user_pair_from_list(usernames))
            else:
                samples = sample(usernames, self.config.SYNC_COUNT)
                return Progress(list=samples, users=self._get_user_pair_from_list(samples))
        elif len(to_check) > self.config.SYNC_COUNT:
            samples = sample(to_check, self.config.SYNC_COUNT)
            return Progress(list=samples, users=self._get_user_pair_from_list(samples))
        else:
            return Progress(list=to_check, users=self._get_user_pair_from_list(to_check))

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

        print('Adding users ...')

        for user in users:
            print(f"Adding {user.username} ...")
            user.get_following(self.twitter_api.client)
            UserDocument.create_from_user_class(user)

        print('Completed adding users')

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

    def _save_from_users(self, users: List[UserPair]):
        """Persist following data to user
        """
        for user in users:
            if user["user"].changed:
                user["document"].following = [user.to_dict()
                                              for user in user["user"].following]
                user["user"].set_unchanged()
                user["document"].save()

    def sync(self):
        """Monitor new following and unfollowing then notify to user
        """
        progress: Progress = self._get_users_to_check()
        print("Checking {}".format(', '.join(progress["list"])))

        client = self.twitter_api.get_new_client()

        for pair in progress["users"]:
            user = pair["user"]
            old = user.following_usernames.copy()
            user.get_following(client)
            new = user.following_usernames.copy()

            new_following = User.new_following(new, old)
            new_unfollowing = User.new_unfollowing(new, old)

            if len(new_following) != 0 or len(new_unfollowing) != 0:
                user.set_changed()
                self._notify_new_following(user, new_following)
                self._notify_new_unfollowing(user, new_unfollowing)

        self._add_usernames_to_saved_progress(progress["list"])
        self._save_from_users(progress["users"])
