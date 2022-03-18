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

    AIRTABLE_API_KEY: str
    AIRTABLE_APP_ID: str
    AIRTABLE_TABLE_LEADERBOARD: str
    AIRTABLE_TABLE_RESULT: str
    AIRTABLE_TABLE_TRACKED_USERS: str
    AIRTABLE_TABLE_KEYWORDS: str

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

        self.WATCHED_USERS = []

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
