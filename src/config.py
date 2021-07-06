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

    GOOGLE_APPLICATION_CREDENTIALS: str
    SPREADSHEET_URL: str

    SYNC_INTERVAL: int

    def __init__(self):
        self.TWITTER_CUSTOMER_KEY = getenv('TWITTER_CUSTOMER_KEY')
        self.TWITTER_CUSTOMER_SECRET = getenv('TWITTER_CUSTOMER_SECRET')
        self.TWITTER_OAUTH_TOKEN = getenv('TWITTER_OAUTH_TOKEN')
        self.TWITTER_OAUTH_SECRET = getenv('TWITTER_OAUTH_SECRET')
        self.TWITTER_BEARER_TOKEN = getenv('TWITTER_BEARER_TOKEN')

        self.MONGODB_DB_NAME = getenv('MONGODB_DB_NAME')
        self.MONGODB_DB_HOST = getenv('MONGODB_DB_HOST')

        self.TELEGRAM_API_ID = int(getenv('TELEGRAM_API_ID'))
        self.TELEGRAM_API_HASH = getenv('TELEGRAM_API_HASH')

        self.WATCHED_USERS = [user.strip()
                              for user in getenv('WATCHED_USERS').split(',')]

        self.GOOGLE_APPLICATION_CREDENTIALS = getenv(
            'GOOGLE_APPLICATION_CREDENTIALS', 'google-credentials.json')
        self.SPREADSHEET_URL = getenv('SPREADSHEET_URL')

        try:
            self.SYNC_INTERVAL = int(getenv('SYNC_INTERVAL', 30))*60
        except ValueError:
            self.SYNC_INTERVAL = 30*60
