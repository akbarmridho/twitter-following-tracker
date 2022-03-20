from typing import Dict, List, TypedDict
from mongoengine.queryset.queryset import QuerySet  # type: ignore
from src import User, Config, UserDocument, UserPair, Scorer, TwitterAPI, Configuration, Airtable, NewFollowing  # type: ignore
from datetime import date, datetime
from random import sample
import logging
import random


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
    airtable: Airtable
    config: Config
    users: List[UserPair]
    scorer: Scorer
    keywords: List[Dict]

    def __init__(self, config: Config):
        self.config = config
        self.twitter_api = TwitterAPI(config)
        self.airtable = Airtable(config)
        self.keywords = self.airtable.get_keywords()

        self.config.WATCHED_USERS.extend(
            [data["Tracked Users"] for data in self.airtable.get_tracked_users()])
        self.scorer = Scorer(self.keywords,
                             self.airtable.get_tracked_users())

    def _initialize(self):
        """Initialize the application setup
        """
        to_sync = self._get_to_sync_users(
            self.config.WATCHED_USERS, UserDocument.get_usernames(UserDocument.objects.only("username").select_related()))

        self._delete_users(to_sync["to_delete"])
        self._add_users(to_sync["to_add"])

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
        usernames = UserDocument.get_usernames(
            UserDocument.objects.only("username").select_related())
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

        logging.info('Adding users to track ...')

        for user in users:
            logging.info(f"Adding {user.username} ...")
            user.get_following(self.twitter_api.client)
            UserDocument.create_from_user_class(user)

        logging.info('Completed adding users')

    def _notify_new_following(self, user: User, usernames: List[str]):
        if len(usernames) == 0:
            return

        metrics = self.twitter_api.get_metrics(usernames)
        today = datetime.now()

        following_data: List[NewFollowing] = []

        for username in usernames:
            created_at: datetime = metrics[username]['created_at']
            followers_count: int = metrics[username]['followers_count']
            url_points, urls = self.scorer.get_url_point(
                metrics[username]["urls"])

            following_data.append(NewFollowing(
                tracked_user=user.username,
                tracked_user_points=self.scorer.get_username_point(
                    user.username),
                followed_user=username,
                followed_at=today,
                created_at=created_at,
                created_at_points=self.scorer.get_timedelta_point(created_at),
                followers_count=followers_count,
                followers_count_points=self.scorer.get_followers_point(
                    followers_count),
                description=metrics[username]["description"],
                description_points=self.scorer.get_keyword_point(
                    metrics[username]["description"]),
                urls=urls,
                url_points=url_points
            ))

        if len(following_data) > 0:
            self.airtable.save_leaderboard(following_data)
            self.airtable.save_raw(following_data)

    def _notify_new_following_from_timeline(self, users: List[Dict]):
        if len(users) == 0:
            return

        metrics = self.twitter_api.get_metrics(
            [user["username"] for user in users])
        today = datetime.now()

        following_data: List[NewFollowing] = []

        for user in users:
            username = user["username"]
            created_at: datetime = metrics[username]['created_at']
            followers_count: int = metrics[username]['followers_count']
            url_points, urls = self.scorer.get_url_point(
                metrics[username]["urls"])

            following_data.append(NewFollowing(
                tracked_user="TIMELINE",
                tracked_user_points=0,
                followed_user=username,
                followed_at=today,
                created_at=created_at,
                created_at_points=self.scorer.get_timedelta_point(created_at),
                followers_count=followers_count,
                followers_count_points=self.scorer.get_followers_point(
                    followers_count),
                description=metrics[username]["description"],
                description_points=self.scorer.get_keyword_point(
                    metrics[username]["description"]),
                urls=urls,
                url_points=url_points
            ))

        if len(following_data) > 0:
            self.airtable.save_leaderboard(following_data)
            self.airtable.save_raw(following_data)
            logging.info(
                f"Added {len(following_data)} users from tweet search")

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

        users_timeline = self.twitter_api.get_search([word["Keywords"] for word in random.sample(
            self.keywords, 6 if len(self.keywords) > 6 else len(self.keywords))])
        self._notify_new_following_from_timeline(users_timeline)

        progress: Progress = self._get_users_to_check()
        logging.info("Checking {}".format(', '.join(progress["list"])))

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
