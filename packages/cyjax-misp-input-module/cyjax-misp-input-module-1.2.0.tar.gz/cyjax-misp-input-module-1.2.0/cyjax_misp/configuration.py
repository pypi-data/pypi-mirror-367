"""This module provides the module configuration."""

import os
import platform
from datetime import timedelta, datetime
from typing import Union
import json

from cyjax import IndicatorOfCompromise
from cyjax.exceptions import UnauthorizedException

from cyjax_misp.misp import Client, MispException

CYJAX_API_KEY = 'cyjax_api'
MISP_URL = 'misp_url'
MISP_SSL = 'misp_ssl'
MISP_API_KEY = 'misp_api_key'
MISP_EVENT_PUBLISHED_FLAG = 'mispevent_published_flag'
LAST_SYNC_TIMESTAMP = 'last_sync_timestamp'
PROXY_URL = 'proxy_url'
PROXY_USERNAME = 'proxy_username'
PROXY_PASSWORD = 'proxy_password'
CONFIG_FILE_PATH = 'cyjax_misp_input.json'


class InvalidConfigurationException(Exception):
    """Exception for invalid configuration."""


class Configuration:  # pylint: disable=E1136
    """Configuration class to load and save the module configuration."""
    def __init__(self):
        """Class constructor."""
        self.config = {}
        self.config_file_path = None

    def load(self):
        """Loads the configuration."""
        # Find config path
        if platform.mac_ver()[0] != '':
            # macOS
            config_path = os.path.join(os.environ['HOME'], 'Library/Preferences')
        else:
            # XDG-compatible
            config_path = os.environ.get('XDG_CONFIG_HOME', os.path.join(os.environ['HOME'], '.config'))
            if not os.path.exists(config_path):
                os.mkdir(config_path)
        self.config_file_path = config_path + '/' + CONFIG_FILE_PATH
        if os.path.isfile(self.config_file_path):
            with open(self.config_file_path, 'r') as json_file:
                self.config = json.load(json_file)

    def get_config_file_path(self) -> str:
        """
        Returns the configuration file path.
        :return: The  configuration file path
        """
        return self.config_file_path

    def get_cyjax_api_key(self) -> Union[str, None]:
        """
        Returns the Cyjax API key.
        :return: The API key.
        """
        return self._get_config(CYJAX_API_KEY)

    def get_misp_api_key(self) -> Union[str, None]:
        """
        Returns the MISP API key.
        :return: The MISP API key.
        """
        return self._get_config(MISP_API_KEY)

    def get_misp_ssl(self) -> bool:
        """
        Returns the MISP SSL flag.
        :return: The MISP SSL flag.
        """
        return bool(self._get_config(MISP_SSL, True))

    def get_misp_url(self) -> Union[str, None]:
        """
        Returns the MISP URL.
        :return: The MISP URL.
        """
        return self._get_config(MISP_URL)

    def get_misp_event_published_flag(self) -> bool:
        """
        Returns the MISP event published flag.
        :return: The MISP event published flag.
        """
        return bool(self._get_config(MISP_EVENT_PUBLISHED_FLAG, False))

    def has_sync_run(self) -> bool:
        """
        Returns True if the module has ever run, False otherwise.
        :return: True if the module has run, False otherwise.
        """
        last_sync_timestamp = self._get_config(LAST_SYNC_TIMESTAMP, None)
        return last_sync_timestamp is not None

    def get_last_sync_timestamp(self) -> Union[str, timedelta]:
        """
        Returns the last sync timestamp.
        :return: The last sync timestamp.
        """
        return self._get_config(LAST_SYNC_TIMESTAMP, timedelta(days=3))

    def save_last_sync_timestamp(self, last_sync_timestamp: datetime):
        """
        Saves the last sync timestamp.
        :param last_sync_timestamp:
        """
        self.config[LAST_SYNC_TIMESTAMP] = last_sync_timestamp.replace(microsecond=0).isoformat()
        self._save_config()

    def set_config(self,  # pylint: disable=R0913
                   cyjax_api_key: str,
                   misp_url: str,
                   misp_api_key: str,
                   misp_ssl: bool,
                   misp_event_published_flag: bool = False):
        """
        Validates and saves the configuration.
        :param cyjax_api_key: The Cyjax API key.
        :param misp_url: The MISP URL.
        :param misp_api_key: The MISP API key.
        :param misp_ssl: The MISP SSL flag.
        :param misp_event_published_flag: The misp_events_published_flag value
        """
        self.config[CYJAX_API_KEY] = cyjax_api_key
        self.config[MISP_URL] = misp_url
        self.config[MISP_API_KEY] = misp_api_key
        self.config[MISP_SSL] = misp_ssl
        self.config[MISP_EVENT_PUBLISHED_FLAG] = misp_event_published_flag

        self.validate()

        # Validate MISP
        try:
            Client(self.config[MISP_URL], self.config[MISP_API_KEY], ssl=self.config[MISP_SSL])
        except MispException as exception:
            raise InvalidConfigurationException(str(exception)) from exception
        # Validate Cyjax API key
        try:
            generator = IndicatorOfCompromise(api_key=self.config[CYJAX_API_KEY]).list(since=timedelta(minutes=1),
                                                                                       limit=1)
            for _ in generator:
                pass
        except UnauthorizedException as exception:
            raise InvalidConfigurationException('Invalid Cyjax API key') from exception

        self._save_config()

    def validate(self):
        """Validates the configuration."""
        if CYJAX_API_KEY not in self.config or not self.config[CYJAX_API_KEY]:
            raise InvalidConfigurationException('The Cyjax API key cannot be empty.')

        if MISP_URL not in self.config or not self.config[MISP_URL]:
            raise InvalidConfigurationException('The MISP URL cannot be empty.')

        if MISP_API_KEY not in self.config or not self.config[MISP_API_KEY]:
            raise InvalidConfigurationException('The MISP API key cannot be empty.')

    def _get_config(self, config_key, default_value=None):
        """

        :param config_key:
        :param default_value:
        :return:
        """
        return self.config[config_key] if config_key in self.config else default_value

    def _save_config(self):
        """Saves the configuration file."""
        with open(self.config_file_path, 'w') as output_file:
            json.dump(self.config, output_file)
