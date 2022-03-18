
from typing import Dict, List, Set, TypedDict
from datetime import datetime, timedelta
from pytz import UTC  # type: ignore
import re


class Word(TypedDict):
    word: str
    points: int


class Account(TypedDict):
    username: str
    points: int


class Scorer:
    keywords: Dict[int, List[Word]]
    accounts: Dict[str, int]
    followers: Dict[int, int]
    creation_date: Dict[int, int]
    url_blacklist: List[str]

    def __init__(self, wordlist: List[Dict], accounts: List[Dict]):
        sanitized = self._sanitize(wordlist)
        self.keywords = {}

        for keyword in sanitized:
            word_count = len(keyword["word"].split(" "))
            if word_count in self.keywords:
                self.keywords[word_count].append(keyword)
            else:
                self.keywords[word_count] = [keyword]

        self.accounts = {}

        for account in accounts:
            if account["Tracked Users"] not in self.accounts:
                self.accounts[account["Tracked Users"]] = account["Points"]

        self.followers = {
            200: 100,
            400: 90,
            600: 80,
            800: 70,
            1000: 60,
            1200: 50,
            1600: 45,
            2000: 40,
            2600: 35,
            3200: 30,
            4000: 25,
            5000: 20,
            6000: 15,
            7000: 10,
            8000: 8,
            10000: 6
        }

        self.creation_date = {
            2: 100,
            4: 90,
            6: 80,
            8: 70,
            10: 60,
            12: 50,
            14: 45,
            16: 40,
            18: 35,
            20: 30,
            24: 25,
            28: 20,
            32: 10,
            36: 10,
            40: 8
        }

        self.url_blacklist = [
            "fb.me", "facebook", "twitter", "instagram", "youtube", "wa.me", "whatsapp", "linkedin", "tiktok", "fb.com"
        ]

    def _sanitize(self, wordlist: List[Dict]):
        words: Set[str] = set()
        result: List[Word] = []

        for keyword in wordlist:
            if keyword["Keywords"].lower() not in words:
                words.add(keyword["Keywords"].lower())
                result.append(
                    Word(word=keyword["Keywords"].lower(), points=keyword["Points"]))

        return result

    def get_followers_point(self, followers_count: int):
        for offset in self.followers.keys():
            if followers_count <= offset:
                return self.followers[offset]

        return 4

    def get_timedelta_point(self, date: datetime):
        for offset in self.creation_date.keys():
            if date > datetime.utcnow().replace(tzinfo=UTC) - timedelta(weeks=offset):
                return self.creation_date[offset]

        return 6

    def get_keyword_point(self, description: str):

        words = description.lower().split(" ")
        points = 0

        for wordlength in self.keywords.keys():
            phrases = [' '.join(words[i:i+wordlength])
                       for i in range(len(words)-wordlength)]

            for phrase in phrases:
                for word in self.keywords[wordlength]:
                    if word["word"] == phrase:
                        points += word["points"]

        return points

    def get_username_point(self, username: str):

        if username in self.accounts:
            return self.accounts[username]

        return 0

    def get_url_point(self, urls: List[str]):
        discord_invite = r'discord(?:\.com|app\.com|\.gg)[\/invite\/]?(?:[a-zA-Z0-9\-]{2,32})'
        telegram_invite = r'(t(elegram)?\.me|telegram\.org)\/([\S]{5,32})\/?'

        regex_discord = re.compile(discord_invite)
        regex_telegram = re.compile(telegram_invite)

        points = 0
        match_urls = []

        for url in urls:
            if len(regex_discord.findall(url)) == 1:
                points += 40
                match_urls.append(f"https://{url}")
            elif len(regex_telegram.findall(url)) == 1:
                points += 10
                match_urls.append(f"https://{url}")
            else:
                valid = True
                for blacklist_url in self.url_blacklist:
                    if blacklist_url in url:
                        valid = False
                        break

                if valid:
                    points += 20
                    match_urls.append(f"https://{url}")

        return points, match_urls

    def get_score(self, description: str, username: str, created_at: datetime, followers_count: int, urls: List[str], inlucde_url=True):
        score = self.get_keyword_point(
            description) + self.get_username_point(username)+self.get_followers_point(followers_count) + self.get_timedelta_point(created_at)

        url_point, match_urls = self.get_url_point(urls)

        score += url_point

        if inlucde_url:
            return score, match_urls

        return score
