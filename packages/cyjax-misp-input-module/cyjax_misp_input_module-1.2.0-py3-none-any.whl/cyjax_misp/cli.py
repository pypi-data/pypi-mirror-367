"""This module provides CLI commands."""

import sys
from datetime import timedelta, datetime
import logging

import cyjax
import pytz
from cyjax import ResponseErrorException, IndicatorOfCompromise, ApiKeyNotFoundException
from cyjax.exceptions import TooManyRequestsException

from cyjax_misp import misp, __version__
from cyjax_misp.configuration import Configuration, InvalidConfigurationException

log = logging.getLogger('cyjax-misp')


configuration = Configuration()
configuration.load()


def setup_misp_module():
    """Sets the MISP module up."""
    print('=== MISP input module for Cyjax Threat Intelligence platform ===\n')

    cyjax_api_key = input('Please provide the Cyjax API key:')
    misp_url = input('Please provide the MISP URL:')
    misp_api_key = input('Please provide the MISP API key:')
    misp_ssl_input = input('Should the MISP SSL be used? [yes/no] (default: yes): ')
    misp_ssl = misp_ssl_input.strip().lower() in ('yes', 'true', '1', 'y', '')
    misp_event_published_flag_input = input('Should the MISP events be published by default? [yes/no] (default: no): ')
    misp_event_published_flag = misp_event_published_flag_input.strip().lower() in ('yes', 'true', '1', 'y')

    try:
        print('Testing connection to Cyjax API...')
        cyjax.api_key = cyjax_api_key
        try:
            cyjax.IndicatorOfCompromise().list(limit=1)
        except Exception as e:
            raise InvalidConfigurationException("Invalid Cyjax API key") from e
        print('Testing connection to MISP...')
        configuration.set_config(cyjax_api_key, misp_url, misp_api_key, misp_ssl, misp_event_published_flag)
        print('Connected to MISP!')
        print("Configuration saved to %s" % (configuration.get_config_file_path()))
    except InvalidConfigurationException as exception:
        print('Error: {}'.format(str(exception)))


def show_version() -> None:
    """
    Prints the MISP module version.
    :returns None:
    """
    print(__version__)


def show_config() -> None:
    """
    Prints the MISP module config.
    :returns None:
    """
    print('Cyjax `cyjax-misp-input-module` configuration:')
    print('  version={}'.format(__version__))
    print('  conf_file_path={}'.format(configuration.get_config_file_path()))
    print('    misp_url={}'.format(configuration.get_misp_url()))
    print('    misp_api_key={}'.format(configuration.get_misp_api_key()))
    print('    misp_ssl={}'.format(configuration.get_misp_ssl()))
    print('    cyjax_api_key={}'.format(configuration.get_cyjax_api_key()))
    print('    last_sync_timestamp={}'.format(configuration.get_last_sync_timestamp()
                                              if configuration.has_sync_run() else 'Never run'))
    print('    misp_event_published_flag={}'.format(configuration.get_misp_event_published_flag()))


def run_misp_module(debug: bool = False):
    """Runs the MISP module.
    :param debug: Whether to enable debug.
    """
    try:
        configuration.validate()
    except InvalidConfigurationException:
        log.error('Please configure the MISP input module with --setup argument.')
        sys.exit(-1)

    misp_client = misp.Client(
        configuration.get_misp_url(),
        configuration.get_misp_api_key(),
        ssl=configuration.get_misp_ssl(),
        debug=debug)

    log.info("Running MISP input module...")
    log.info("Using configuration file %s", configuration.get_config_file_path())
    added_indicator_count = 0
    try:
        last_sync_timestamp = configuration.get_last_sync_timestamp()
        if isinstance(last_sync_timestamp, timedelta):
            last_sync_timestamp = datetime.now(tz=pytz.UTC) - last_sync_timestamp
        log.info("Checking indicators since %s", last_sync_timestamp)

        new_sync_timestamp = datetime.now(tz=pytz.UTC)
        cyjax.api_key = configuration.get_cyjax_api_key()

        for indicator in IndicatorOfCompromise().list(since=configuration.get_last_sync_timestamp()):
            added_indicator_count += 1
            log.debug("Processing indicator %s (%s)", indicator['value'], indicator['type'])
            misp_client.save_indicator(indicator)

        configuration.save_last_sync_timestamp(new_sync_timestamp)
        log.info("Added %s indicators", added_indicator_count)

        if added_indicator_count > 0 and configuration.get_misp_event_published_flag() is True:
            log.info("Publishing MISP events...")
            published_events = misp_client.publish_events()
            log.info("Published %s events", published_events)
    except ResponseErrorException:
        log.error("Error fetching indicators")
    except ApiKeyNotFoundException:
        log.error("Please setup an API key")
    except TooManyRequestsException:
        log.error("Rate limit exceeded")
