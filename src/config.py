from os import getenv
from typing import List


class Config:
    TWITTER_CUSTOMER_KEY: str = ''
    TWITTER_CUSTOMER_SECRET: str = ''
    TWITTER_OAUTH_TOKEN: str = ''
    TWITTER_OAUTH_SECRET: str = ''
    TWITTER_BEARER_TOKEN: str = ''

    MONGODB_DB_NAME: str
    MONGODB_DB_HOST: str

    TELEGRAM_API_ID: int
    TELEGRAM_API_HASH: str

    WATCHED_USERS: List[str]

    # GOOGLE_APPLICATION_CREDENTIALS: str
    # SPREADSHEET_URL: str

    AIRTABLE_API_KEY: str
    AIRTABLE_APP_ID: str
    AIRTABLE_TABLE_LEADERBOARD: str
    AIRTABLE_TABLE_RESULT: str
    AIRTABLE_TABLE_TRACKED_USERS: str
    AIRTABLE_TABLE_KEYWORDS: str

    # OFFSET_FOLLOWERS: int = 5000
    # OFFSET_MONTHS: int = 12

    SYNC_INTERVAL: int
    SYNC_COUNT: int = 4

    SCORE_OFFSET: int = 0

    def __init__(self):
        self.TWITTER_CUSTOMER_KEY = getenv('TWITTER_CUSTOMER_KEY')
        self.TWITTER_CUSTOMER_SECRET = getenv('TWITTER_CUSTOMER_SECRET')
        self.TWITTER_OAUTH_TOKEN = getenv('TWITTER_OAUTH_TOKEN')
        self.TWITTER_OAUTH_SECRET = getenv('TWITTER_OAUTH_SECRET')
        self.TWITTER_BEARER_TOKEN = getenv('TWITTER_BEARER_TOKEN')

        self.MONGODB_DB_NAME = getenv('MONGODB_DB_NAME')
        self.MONGODB_DB_HOST = getenv('MONGODB_DB_HOST')

        # self.TELEGRAM_API_ID = int(getenv('TELEGRAM_API_ID'))
        # self.TELEGRAM_API_HASH = getenv('TELEGRAM_API_HASH')

        self.WATCHED_USERS = []

        # self.WATCHED_USERS = [user.strip()
        #                       for user in getenv('WATCHED_USERS').split(',')]

        # self.GOOGLE_APPLICATION_CREDENTIALS = getenv(
        #     'GOOGLE_APPLICATION_CREDENTIALS', 'google-credentials.json')
        # self.SPREADSHEET_URL = getenv('SPREADSHEET_URL')

        self.AIRTABLE_API_KEY = getenv('AIRTABLE_API_KEY')
        self.AIRTABLE_APP_ID = getenv('AIRTABLE_APP_ID')
        self.AIRTABLE_TABLE_LEADERBOARD = getenv('AIRTABLE_TABLE_LEADERBOARD')
        self.AIRTABLE_TABLE_RESULT = getenv('AIRTABLE_TABLE_RESULT')
        self.AIRTABLE_TABLE_TRACKED_USERS = getenv(
            'AIRTABLE_TABLE_TRACKED_USERS')
        self.AIRTABLE_TABLE_KEYWORDS = getenv('AIRTABLE_TABLE_KEYWORDS')

        try:
            self.SYNC_INTERVAL = int(getenv('SYNC_INTERVAL', 30))*60
        except ValueError:
            self.SYNC_INTERVAL = 30*60

        try:
            self.SYNC_COUNT = int(getenv('SYNC_COUNT', 4))
        except ValueError:
            self.SYNC_COUNT = 4

        self.SCORE_OFFSET = int(getenv("SCORE_OFFSET", 0))

        # try:
        #     self.OFFSET_FOLLOWERS = int(getenv('OFFSET_FOLLOWERS', 5000))
        # except ValueError:
        #     self.OFFSET_FOLLOWERS = 5000

        # try:
        #     self.OFFSET_MONTHS = int(getenv('OFFSET_MONTHS', 12))
        # except ValueError:
        #     self.OFFSET_MONTHS = 12
