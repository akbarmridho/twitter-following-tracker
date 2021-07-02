from typing import List
from mongoengine.queryset.queryset import QuerySet
from telethon.sync import TelegramClient
from telemongo import MongoSession
from telethon.tl.custom import Dialog
from telethon.tl.types import Channel, InputPeerChannel
from src import Config, Configuration
from mongoengine import QuerySet
import logging
import traceback


class Telegram:
    client: TelegramClient = None
    chats: List[Dialog]
    groups: List[Dialog]
    target_group: Dialog
    target_group_entity: Channel
    target_group_input_entity: InputPeerChannel

    def __init__(self, config: Config):
        """Automatically connect through Telegram API upon creation"""

        telegram_session = MongoSession(
            config.MONGODB_DB_NAME, host=config.MONGODB_DB_HOST)
        self.client = TelegramClient(
            telegram_session, config.TELEGRAM_API_ID, config.TELEGRAM_API_HASH).start()

    def _get_recent_chat(self):
        """Get receng chats including personal, group, and channel chats"""
        self.chats = self.client.get_dialogs()

    def _get_group_list(self):
        """Get list of channel from dialogue list"""
        if not self.chats:
            self._get_recent_chat()

        self.groups = []

        for chat in self.chats:
            if chat.is_channel:
                self.groups.append(chat)

    def _select_group(self):
        """Select group for upcoming action"""
        if not self.groups:
            self._get_group_list()

        print('Choose a channel for notification to be sent')
        print('Please note that you must an admin of that channel')
        i = 0

        for group in self.groups:
            print(str(i) + '- ' + group.title)
            i += 1

        target_group_index = int(input('Enter a number: '))
        self.target_group = self.groups[target_group_index]
        self.target_group_entity = self.target_group.entity
        self.target_group_input_entity = self.target_group.input_entity

    def _set_channel(self):
        """Save channel id and channel hash into mongodb database"""
        channel_id = self.target_group_input_entity.channel_id
        channel_hash = self.target_group_input_entity.access_hash

        ids: QuerySet = Configuration.objects(key='TELEGRAM_CHANNEL_ID')
        hashes: QuerySet = Configuration.objects(key='TELEGRAM_CHANNEL_HASH')

        # delete old configuration
        ids.delete()
        hashes.delete()

        Configuration(key='TELEGRAM_CHANNEL_ID', value=str(channel_id)).save()
        Configuration(key='TELEGRAM_CHANNEL_HASH',
                      value=str(channel_hash)).save()

    def _get_channel(self) -> Channel:
        """Get channel entity or input entity from mongodb database"""
        ids: QuerySet = Configuration.objects(key='TELEGRAM_CHANNEL_ID')
        hashes: QuerySet = Configuration.objects(key='TELEGRAM_CHANNEL_HASH')

        if ids.count() == 0 or hashes.count() == 0:
            raise Exception('Please set target channel first')

        channel_id = int(ids.first().value)
        channel_hash = int(hashes.first().value)

        channel: Channel = self.client.get_entity(
            InputPeerChannel(channel_id, channel_hash))

        self.target_group_entity = channel

        return channel

    def initialize(self):
        """Initialize the telegram module"""
        self._get_channel()

    def setup(self):
        """Start session setup and channel target"""
        self._get_recent_chat()
        self._get_group_list()
        self._select_group()
        self._set_channel()

    def send_message(self, message: str):
        """Send message to channel"""
        if not self.target_group_entity:
            self._get_channel()

        try:
            self.client.send_message(self.target_group_entity, message=message)
        except Exception:
            logging.exception(traceback.format_exc())
