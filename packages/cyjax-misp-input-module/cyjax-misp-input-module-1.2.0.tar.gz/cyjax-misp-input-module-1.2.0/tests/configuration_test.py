import unittest
from unittest.mock import patch, MagicMock

from cyjax_misp.configuration import Configuration, CYJAX_API_KEY, MISP_URL, MISP_API_KEY, \
    InvalidConfigurationException, CONFIG_FILE_PATH, MISP_EVENT_PUBLISHED_FLAG, MISP_SSL


class ConfigurationTest(unittest.TestCase):
    def setUp(self):
        self.configuration = Configuration()
        self.configuration.config[CYJAX_API_KEY] = 'test-cyjax-key'
        self.configuration.config[MISP_URL] = 'http://misp-url.com'
        self.configuration.config[MISP_API_KEY] = 'test-misp-key'
        # Set config file path to avoid NoneType error
        self.configuration.config_file_path = '/tmp/test_config.json'

    def test_validate_with_no_cyjax_key(self):
        del self.configuration.config[CYJAX_API_KEY]

        with self.assertRaises(InvalidConfigurationException) as context:
            self.configuration.validate()
        self.assertEqual('The Cyjax API key cannot be empty.', str(context.exception))

    def test_validate_with_empty_cyjax_key(self):
        self.configuration.config[CYJAX_API_KEY] = ''

        with self.assertRaises(InvalidConfigurationException) as context:
            self.configuration.validate()
        self.assertEqual('The Cyjax API key cannot be empty.', str(context.exception))

    def test_validate_with_no_misp_url(self):
        del self.configuration.config[MISP_URL]

        with self.assertRaises(InvalidConfigurationException) as context:
            self.configuration.validate()
        self.assertEqual('The MISP URL cannot be empty.', str(context.exception))

    def test_validate_with_empty_misp_url(self):
        self.configuration.config[MISP_URL] = ''

        with self.assertRaises(InvalidConfigurationException) as context:
            self.configuration.validate()
        self.assertEqual('The MISP URL cannot be empty.', str(context.exception))

    def test_validate_with_no_misp_key(self):
        del self.configuration.config[MISP_API_KEY]

        with self.assertRaises(InvalidConfigurationException) as context:
            self.configuration.validate()
        self.assertEqual('The MISP API key cannot be empty.', str(context.exception))

    def test_validate_with_empty_misp_key(self):
        self.configuration.config[MISP_API_KEY] = ''

        with self.assertRaises(InvalidConfigurationException) as context:
            self.configuration.validate()
        self.assertEqual('The MISP API key cannot be empty.', str(context.exception))

    def test_get_cyjax_api_key(self):
        self.assertEqual('test-cyjax-key', self.configuration.get_cyjax_api_key())

    def test_get_misp_url(self):
        self.assertEqual('http://misp-url.com', self.configuration.get_misp_url())

    def test_get_misp_api_key(self):
        self.assertEqual('test-misp-key', self.configuration.get_misp_api_key())

    def test_get_misp_ssl_not_set(self):
        """Test that when misp_ssl is not set, it returns True (default)"""
        self.assertTrue(self.configuration.get_misp_ssl())

    def test_get_misp_ssl_false(self):
        """Test that when misp_ssl is set to False, it returns False"""
        self.configuration.config[MISP_SSL] = False
        self.assertFalse(self.configuration.get_misp_ssl())

    def test_get_misp_ssl_true(self):
        """Test that when misp_ssl is set to True, it returns True"""
        self.configuration.config[MISP_SSL] = True
        self.assertTrue(self.configuration.get_misp_ssl())

    def test_get_misp_event_published_flag_not_set(self):
        """Test that when misp_event_published_flag is not set, it returns None"""
        self.assertFalse(self.configuration.get_misp_event_published_flag())

    def test_get_misp_event_published_flag_false(self):
        """Test that when misp_event_published_flag is set to False, it returns False"""
        self.configuration.config[MISP_EVENT_PUBLISHED_FLAG] = False
        self.assertFalse(self.configuration.get_misp_event_published_flag())

    def test_get_misp_event_published_flag_true(self):
        """Test that when misp_event_published_flag is set to True, it returns True"""
        self.configuration.config[MISP_EVENT_PUBLISHED_FLAG] = True
        self.assertTrue(self.configuration.get_misp_event_published_flag())

    @patch('cyjax_misp.configuration.Client')
    @patch('cyjax_misp.configuration.IndicatorOfCompromise')
    def test_set_config_with_misp_ssl_true(self, mock_indicator, mock_client):
        """Test that set_config properly stores misp_ssl as True"""
        # Mock the indicator list method to return an empty generator
        mock_indicator_instance = MagicMock()
        mock_indicator_instance.list.return_value = iter([])
        mock_indicator.return_value = mock_indicator_instance
        
        self.configuration.set_config('test-cyjax-key', 'http://misp-url.com', 'test-misp-key', True, False)
        self.assertTrue(self.configuration.get_misp_ssl())

    @patch('cyjax_misp.configuration.Client')
    @patch('cyjax_misp.configuration.IndicatorOfCompromise')
    def test_set_config_with_misp_ssl_false(self, mock_indicator, mock_client):
        """Test that set_config properly stores misp_ssl as False"""
        # Mock the indicator list method to return an empty generator
        mock_indicator_instance = MagicMock()
        mock_indicator_instance.list.return_value = iter([])
        mock_indicator.return_value = mock_indicator_instance
        
        self.configuration.set_config('test-cyjax-key', 'http://misp-url.com', 'test-misp-key', False, False)
        self.assertFalse(self.configuration.get_misp_ssl())

    @patch('cyjax_misp.configuration.Client')
    @patch('cyjax_misp.configuration.IndicatorOfCompromise')
    def test_set_config_with_misp_event_published_flag_false(self, mock_indicator, mock_client):
        """Test that set_config properly stores misp_event_published_flag as False"""
        # Mock the indicator list method to return an empty generator
        mock_indicator_instance = MagicMock()
        mock_indicator_instance.list.return_value = iter([])
        mock_indicator.return_value = mock_indicator_instance
        
        self.configuration.set_config('test-cyjax-key', 'http://misp-url.com', 'test-misp-key', True, False)
        self.assertFalse(self.configuration.get_misp_event_published_flag())

    @patch('cyjax_misp.configuration.Client')
    @patch('cyjax_misp.configuration.IndicatorOfCompromise')
    def test_set_config_with_misp_event_published_flag_true(self, mock_indicator, mock_client):
        """Test that set_config properly stores misp_event_published_flag as True"""
        # Mock the indicator list method to return an empty generator
        mock_indicator_instance = MagicMock()
        mock_indicator_instance.list.return_value = iter([])
        mock_indicator.return_value = mock_indicator_instance
        
        self.configuration.set_config('test-cyjax-key', 'http://misp-url.com', 'test-misp-key', True, True)
        self.assertTrue(self.configuration.get_misp_event_published_flag())

    def test_get_config_file_path(self):
        self.configuration.config_file_path = '/test/' + CONFIG_FILE_PATH
        self.assertEqual('/test/' + CONFIG_FILE_PATH, self.configuration.get_config_file_path())
