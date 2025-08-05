
import unittest
import sys
from datetime import datetime, timedelta
from unittest.mock import call, patch, MagicMock
import pytz

from cyjax_misp.cli import run_misp_module
from cyjax_misp.configuration import Configuration, InvalidConfigurationException
from cyjax_misp.misp import Client


class RunTest(unittest.TestCase):
    """Integration tests for the run_misp_module function."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_indicators = [
            {
                'type': 'Email',
                'value': 'test@example.com',
                'discovered_at': '2023-01-01T10:00:00+0000',
                'source': 'https://cymon.com/incident/report/view?id=1234',
                'description': 'Test indicator 1',
                'handling_condition': 'GREEN'
            },
            {
                'type': 'IPv4',
                'value': '192.168.1.1',
                'discovered_at': '2023-01-01T11:00:00+0000',
                'source': 'https://cymon.com/incident/report/view?id=5678',
                'description': 'Test indicator 2',
                'handling_condition': 'AMBER'
            }
        ]

    @patch('cyjax_misp.cli.configuration')
    @patch('cyjax_misp.cli.misp.Client')
    @patch('cyjax_misp.cli.IndicatorOfCompromise')
    @patch('cyjax_misp.cli.cyjax')
    def test_run_misp_module_successful_with_indicators(self, mock_cyjax, mock_indicator_class, mock_misp_client, mock_config):
        """Test successful run with indicators found."""
        # Mock configuration
        mock_config.validate.return_value = None
        mock_config.get_misp_url.return_value = 'http://misp.example.com'
        mock_config.get_misp_api_key.return_value = 'misp-api-key'
        mock_config.get_misp_ssl.return_value = True
        mock_config.get_misp_event_published_flag.return_value = False
        mock_config.get_last_sync_timestamp.return_value = timedelta(hours=1)
        mock_config.get_cyjax_api_key.return_value = 'cyjax-api-key'
        mock_config.get_config_file_path.return_value = '/path/to/config.json'

        # Mock MISP client
        mock_misp_instance = MagicMock()
        mock_misp_client.return_value = mock_misp_instance

        # Mock Cyjax API
        mock_indicator_instance = MagicMock()
        mock_indicator_instance.list.return_value = self.mock_indicators
        mock_indicator_class.return_value = mock_indicator_instance

        # Run the function
        run_misp_module()

        # Verify configuration validation
        mock_config.validate.assert_called_once()

        # Verify MISP client creation
        mock_misp_client.assert_called_once_with(
            'http://misp.example.com',
            'misp-api-key',
            ssl=True,
            debug=False
        )

        # Verify Cyjax API key setting
        self.assertEqual(mock_cyjax.api_key, 'cyjax-api-key')

        # Verify indicators were processed
        mock_indicator_instance.list.assert_called_once_with(since=timedelta(hours=1))
        self.assertEqual(mock_misp_instance.save_indicator.call_count, 2)
        mock_misp_instance.save_indicator.assert_any_call(self.mock_indicators[0])
        mock_misp_instance.save_indicator.assert_any_call(self.mock_indicators[1])

        # Verify timestamp was saved
        mock_config.save_last_sync_timestamp.assert_called_once()

        # Verify publish was not called (since published flag is False)
        mock_misp_instance.publish_events.assert_not_called()

    @patch('cyjax_misp.cli.configuration')
    @patch('cyjax_misp.cli.misp.Client')
    @patch('cyjax_misp.cli.IndicatorOfCompromise')
    @patch('cyjax_misp.cli.cyjax')
    def test_run_misp_module_successful_with_published_flag(self, mock_cyjax, mock_indicator_class, mock_misp_client, mock_config):
        """Test successful run with published flag enabled."""
        # Mock configuration
        mock_config.validate.return_value = None
        mock_config.get_misp_url.return_value = 'http://misp.example.com'
        mock_config.get_misp_api_key.return_value = 'misp-api-key'
        mock_config.get_misp_ssl.return_value = True
        mock_config.get_misp_event_published_flag.return_value = True
        mock_config.get_last_sync_timestamp.return_value = timedelta(hours=1)
        mock_config.get_cyjax_api_key.return_value = 'cyjax-api-key'
        mock_config.get_config_file_path.return_value = '/path/to/config.json'

        # Mock MISP client
        mock_misp_instance = MagicMock()
        mock_misp_instance.publish_events.return_value = 2
        mock_misp_client.return_value = mock_misp_instance

        # Mock Cyjax API
        mock_indicator_instance = MagicMock()
        mock_indicator_instance.list.return_value = self.mock_indicators
        mock_indicator_class.return_value = mock_indicator_instance

        # Run the function
        run_misp_module()

        # Verify published flag was set
        self.assertTrue(mock_misp_instance.misp_event_published_flag)

        # Verify publish was called
        mock_misp_instance.publish_events.assert_called_once()

    @patch('cyjax_misp.cli.configuration')
    @patch('cyjax_misp.cli.misp.Client')
    @patch('cyjax_misp.cli.IndicatorOfCompromise')
    @patch('cyjax_misp.cli.cyjax')
    def test_run_misp_module_no_indicators(self, mock_cyjax, mock_indicator_class, mock_misp_client, mock_config):
        """Test run when no indicators are found."""
        # Mock configuration
        mock_config.validate.return_value = None
        mock_config.get_misp_url.return_value = 'http://misp.example.com'
        mock_config.get_misp_api_key.return_value = 'misp-api-key'
        mock_config.get_misp_ssl.return_value = True
        mock_config.get_misp_event_published_flag.return_value = True
        mock_config.get_last_sync_timestamp.return_value = timedelta(hours=1)
        mock_config.get_cyjax_api_key.return_value = 'cyjax-api-key'
        mock_config.get_config_file_path.return_value = '/path/to/config.json'

        # Mock MISP client
        mock_misp_instance = MagicMock()
        mock_misp_client.return_value = mock_misp_instance

        # Mock Cyjax API - no indicators
        mock_indicator_instance = MagicMock()
        mock_indicator_instance.list.return_value = []
        mock_indicator_class.return_value = mock_indicator_instance

        # Run the function
        run_misp_module()

        # Verify no indicators were processed
        mock_indicator_instance.list.assert_called_once_with(since=timedelta(hours=1))
        mock_misp_instance.save_indicator.assert_not_called()

        # Verify publish was not called (no indicators added)
        mock_misp_instance.publish_events.assert_not_called()

    @patch('cyjax_misp.cli.configuration')
    @patch('cyjax_misp.cli.sys')
    @patch('cyjax_misp.cli.misp.Client')
    @patch('cyjax_misp.cli.IndicatorOfCompromise')
    def test_run_misp_module_invalid_configuration(self, mock_indicator_class, mock_misp_client, mock_sys, mock_config):
        """Test run with invalid configuration."""
        # Mock configuration to raise exception
        mock_config.validate.side_effect = InvalidConfigurationException("Invalid config")

        # Run the function
        run_misp_module()

        # Verify sys.exit was called
        mock_sys.exit.assert_called_once_with(-1)

    @patch('cyjax_misp.cli.configuration')
    @patch('cyjax_misp.cli.misp.Client')
    @patch('cyjax_misp.cli.IndicatorOfCompromise')
    @patch('cyjax_misp.cli.cyjax')
    def test_run_misp_module_response_error(self, mock_cyjax, mock_indicator_class, mock_misp_client, mock_config):
        """Test run when Cyjax API returns ResponseErrorException."""
        from cyjax import ResponseErrorException

        # Mock configuration
        mock_config.validate.return_value = None
        mock_config.get_misp_url.return_value = 'http://misp.example.com'
        mock_config.get_misp_api_key.return_value = 'misp-api-key'
        mock_config.get_misp_ssl.return_value = True
        mock_config.get_misp_event_published_flag.return_value = False
        mock_config.get_last_sync_timestamp.return_value = timedelta(hours=1)
        mock_config.get_cyjax_api_key.return_value = 'cyjax-api-key'
        mock_config.get_config_file_path.return_value = '/path/to/config.json'

        # Mock MISP client
        mock_misp_instance = MagicMock()
        mock_misp_client.return_value = mock_misp_instance

        # Mock Cyjax API to raise exception
        mock_indicator_instance = MagicMock()
        mock_indicator_instance.list.side_effect = ResponseErrorException(500, "API Error")
        mock_indicator_class.return_value = mock_indicator_instance

        # Run the function
        run_misp_module()

        # Verify no indicators were processed
        mock_misp_instance.save_indicator.assert_not_called()

    @patch('cyjax_misp.cli.configuration')
    @patch('cyjax_misp.cli.misp.Client')
    @patch('cyjax_misp.cli.IndicatorOfCompromise')
    @patch('cyjax_misp.cli.cyjax')
    def test_run_misp_module_api_key_not_found(self, mock_cyjax, mock_indicator_class, mock_misp_client, mock_config):
        """Test run when Cyjax API returns ApiKeyNotFoundException."""
        from cyjax import ApiKeyNotFoundException

        # Mock configuration
        mock_config.validate.return_value = None
        mock_config.get_misp_url.return_value = 'http://misp.example.com'
        mock_config.get_misp_api_key.return_value = 'misp-api-key'
        mock_config.get_misp_ssl.return_value = True
        mock_config.get_misp_event_published_flag.return_value = False
        mock_config.get_last_sync_timestamp.return_value = timedelta(hours=1)
        mock_config.get_cyjax_api_key.return_value = 'cyjax-api-key'
        mock_config.get_config_file_path.return_value = '/path/to/config.json'

        # Mock MISP client
        mock_misp_instance = MagicMock()
        mock_misp_client.return_value = mock_misp_instance

        # Mock Cyjax API to raise exception
        mock_indicator_instance = MagicMock()
        mock_indicator_instance.list.side_effect = ApiKeyNotFoundException()
        mock_indicator_class.return_value = mock_indicator_instance

        # Run the function
        run_misp_module()

        # Verify no indicators were processed
        mock_misp_instance.save_indicator.assert_not_called()

    @patch('cyjax_misp.cli.configuration')
    @patch('cyjax_misp.cli.misp.Client')
    @patch('cyjax_misp.cli.IndicatorOfCompromise')
    @patch('cyjax_misp.cli.cyjax')
    def test_run_misp_module_too_many_requests(self, mock_cyjax, mock_indicator_class, mock_misp_client, mock_config):
        """Test run when Cyjax API returns TooManyRequestsException."""
        from cyjax.exceptions import TooManyRequestsException

        # Mock configuration
        mock_config.validate.return_value = None
        mock_config.get_misp_url.return_value = 'http://misp.example.com'
        mock_config.get_misp_api_key.return_value = 'misp-api-key'
        mock_config.get_misp_ssl.return_value = True
        mock_config.get_misp_event_published_flag.return_value = False
        mock_config.get_last_sync_timestamp.return_value = timedelta(hours=1)
        mock_config.get_cyjax_api_key.return_value = 'cyjax-api-key'
        mock_config.get_config_file_path.return_value = '/path/to/config.json'

        # Mock MISP client
        mock_misp_instance = MagicMock()
        mock_misp_client.return_value = mock_misp_instance

        # Mock Cyjax API to raise exception
        mock_indicator_instance = MagicMock()
        mock_indicator_instance.list.side_effect = TooManyRequestsException()
        mock_indicator_class.return_value = mock_indicator_instance

        # Run the function
        run_misp_module()

        # Verify no indicators were processed
        mock_misp_instance.save_indicator.assert_not_called()

    @patch('cyjax_misp.cli.configuration')
    @patch('cyjax_misp.cli.misp.Client')
    @patch('cyjax_misp.cli.IndicatorOfCompromise')
    @patch('cyjax_misp.cli.cyjax')
    def test_run_misp_module_with_debug_enabled(self, mock_cyjax, mock_indicator_class, mock_misp_client, mock_config):
        """Test run with debug mode enabled."""
        # Mock configuration
        mock_config.validate.return_value = None
        mock_config.get_misp_url.return_value = 'http://misp.example.com'
        mock_config.get_misp_api_key.return_value = 'misp-api-key'
        mock_config.get_misp_ssl.return_value = True
        mock_config.get_misp_event_published_flag.return_value = False
        mock_config.get_last_sync_timestamp.return_value = timedelta(hours=1)
        mock_config.get_cyjax_api_key.return_value = 'cyjax-api-key'
        mock_config.get_config_file_path.return_value = '/path/to/config.json'

        # Mock MISP client
        mock_misp_instance = MagicMock()
        mock_misp_client.return_value = mock_misp_instance

        # Mock Cyjax API
        mock_indicator_instance = MagicMock()
        mock_indicator_instance.list.return_value = self.mock_indicators
        mock_indicator_class.return_value = mock_indicator_instance

        # Run the function with debug=True
        run_misp_module(debug=True)

        # Verify MISP client was created with debug=True
        mock_misp_client.assert_called_once_with(
            'http://misp.example.com',
            'misp-api-key',
            ssl=True,
            debug=True
        )

    @patch('cyjax_misp.cli.configuration')
    @patch('cyjax_misp.cli.misp.Client')
    @patch('cyjax_misp.cli.IndicatorOfCompromise')
    @patch('cyjax_misp.cli.cyjax')
    def test_run_misp_module_with_datetime_timestamp(self, mock_cyjax, mock_indicator_class, mock_misp_client, mock_config):
        """Test run when last_sync_timestamp is a datetime object."""
        # Mock configuration
        mock_config.validate.return_value = None
        mock_config.get_misp_url.return_value = 'http://misp.example.com'
        mock_config.get_misp_api_key.return_value = 'misp-api-key'
        mock_config.get_misp_ssl.return_value = True
        mock_config.get_misp_event_published_flag.return_value = False
        mock_config.get_last_sync_timestamp.return_value = datetime.now(tz=pytz.UTC) - timedelta(hours=1)
        mock_config.get_cyjax_api_key.return_value = 'cyjax-api-key'
        mock_config.get_config_file_path.return_value = '/path/to/config.json'

        # Mock MISP client
        mock_misp_instance = MagicMock()
        mock_misp_client.return_value = mock_misp_instance

        # Mock Cyjax API
        mock_indicator_instance = MagicMock()
        mock_indicator_instance.list.return_value = self.mock_indicators
        mock_indicator_class.return_value = mock_indicator_instance

        # Run the function
        run_misp_module()

        # Verify indicators were processed
        mock_indicator_instance.list.assert_called_once()
        self.assertEqual(mock_misp_instance.save_indicator.call_count, 2)

    @patch('cyjax_misp.cli.configuration')
    @patch('cyjax_misp.cli.misp.Client')
    @patch('cyjax_misp.cli.IndicatorOfCompromise')
    @patch('cyjax_misp.cli.cyjax')
    def test_run_misp_module_with_ssl_disabled(self, mock_cyjax, mock_indicator_class, mock_misp_client, mock_config):
        """Test run with SSL disabled."""
        # Mock configuration
        mock_config.validate.return_value = None
        mock_config.get_misp_url.return_value = 'http://misp.example.com'
        mock_config.get_misp_api_key.return_value = 'misp-api-key'
        mock_config.get_misp_ssl.return_value = False
        mock_config.get_misp_event_published_flag.return_value = False
        mock_config.get_last_sync_timestamp.return_value = timedelta(hours=1)
        mock_config.get_cyjax_api_key.return_value = 'cyjax-api-key'
        mock_config.get_config_file_path.return_value = '/path/to/config.json'

        # Mock MISP client
        mock_misp_instance = MagicMock()
        mock_misp_client.return_value = mock_misp_instance

        # Mock Cyjax API
        mock_indicator_instance = MagicMock()
        mock_indicator_instance.list.return_value = self.mock_indicators
        mock_indicator_class.return_value = mock_indicator_instance

        # Run the function
        run_misp_module()

        # Verify MISP client was created with ssl=False
        mock_misp_client.assert_called_once_with(
            'http://misp.example.com',
            'misp-api-key',
            ssl=False,
            debug=False
        )
