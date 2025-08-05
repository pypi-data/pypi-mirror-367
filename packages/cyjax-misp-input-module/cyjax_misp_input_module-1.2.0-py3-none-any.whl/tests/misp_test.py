import unittest
from datetime import datetime
from unittest.mock import call, patch, MagicMock
from uuid import UUID

import pymisp
import cyjax
from pymisp import MISPAttribute, MISPEvent

from cyjax_misp.misp import Client, misp_org


class MISPEventMatcher(MISPEvent):
    def __eq__(self, other: MISPEvent):
        return self.info == other.info and self.Orgc == other.Orgc and self.date == other.date and self.analysis == other.analysis and self.published == other.published


class MISPAttributeMatcher(MISPAttribute):
    def __eq__(self, other: MISPAttribute):
        return self.type == other.type and self.value == self.value and self.timestamp == self.timestamp


class AnyClass:
    def __init__(self, cls):
        self.cls = cls

    def __eq__(self, other):
        return isinstance(other, self.cls)


class MockedIncidentReport(cyjax.resources.incident_report.IncidentReportDto):
    def __init__(self, **kwargs):
        super(MockedIncidentReport, self).__init__(id=2334, **kwargs)


EVENT_UUID = '2c5cdb40-bb3f-4178-9fe9-998759cca32e'
INDICATOR_TIMESTAMP = '2020-12-07T08:42:54+0000'


@patch('pymisp.PyMISP')
class ClientTest(unittest.TestCase):

    def _create_misp_event(self, event_uuid: str, title: str, timestamp: str, published: bool = False) -> MISPEvent:
        misp_event = MISPEventMatcher()
        misp_event.uuid = event_uuid
        misp_event.Orgc = misp_org
        misp_event.from_dict(info=title, date=timestamp, analysis=2, published=published)
        return misp_event

    def _create_misp_attribute(self, indicator_type: str, value: str, timestamp: str) -> MISPAttribute:
        attribute = MISPAttributeMatcher()
        attribute.from_dict(value=value, type=indicator_type,
                            timestamp=datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S%z'))
        return attribute

    def _create_indicator(self, indicator_type: str, value: str, source: str = None):
        return {
            'type': indicator_type,
            'value': value,
            'discovered_at': INDICATOR_TIMESTAMP,
            'source': source if source else 'https://cymon.com/incident/report/view?id=2334',
            'description': 'This is a test',
            'handling_condition': 'GREEN'
        }

    def test_client_constructor_with_ssl_true(self, pymisp_mock):
        """Test that Client constructor passes ssl=True to PyMISP"""
        Client('http://localhost:8888', 'test-misp-key', ssl=True)
        pymisp_mock.assert_called_with('http://localhost:8888', 'test-misp-key', ssl=True)

    def test_client_constructor_with_ssl_false(self, pymisp_mock):
        """Test that Client constructor passes ssl=False to PyMISP"""
        Client('http://localhost:8888', 'test-misp-key', ssl=False)
        pymisp_mock.assert_called_with('http://localhost:8888', 'test-misp-key', ssl=False)

    def test_client_constructor_with_ssl_default(self, pymisp_mock):
        """Test that Client constructor passes ssl=True (default) to PyMISP"""
        Client('http://localhost:8888', 'test-misp-key')
        pymisp_mock.assert_called_with('http://localhost:8888', 'test-misp-key', ssl=True)

    @patch('cyjax.IncidentReport.one', return_value=MockedIncidentReport())
    def test_save_indicator_with_published_flag_not_set(self, cyjax_get_one_mock, pymisp_mock):
        """Test that when misp_event_published_flag is not set, events are created with published=False"""
        self.client = Client('http://localhost:8888', 'test-misp-key')
        pymisp_mock.return_value.search.return_value = []
        self.client.save_indicator(self._create_indicator('Email', 'test@domain.com'))

        pymisp_mock.return_value.add_event.assert_called_with(
            self._create_misp_event(EVENT_UUID, 'This is a test',
                                    INDICATOR_TIMESTAMP, published=False))
        pymisp_mock.return_value.add_attribute.assert_called_with(AnyClass(str),
                                                                  self._create_misp_attribute('email-src',
                                                                                              'test@domain.com',
                                                                                              INDICATOR_TIMESTAMP))
        cyjax_get_one_mock.assert_called_once_with(2334)

    @patch('cyjax.IncidentReport.one', side_effect=MagicMock)
    def test_save_indicator_with_existing_event(self, cyjax_get_one_mock, pymisp_mock):
        self.client = Client('http://localhost:8888', 'test-misp-key')
        pymisp_mock.return_value.search.return_value = [{'Event': {'uuid': EVENT_UUID}}]
        self.client.save_indicator(self._create_indicator('Email', 'test@domain.com'))

        pymisp_mock.return_value.add_event.assert_not_called()
        pymisp_mock.return_value.add_attribute.assert_called_with(EVENT_UUID,
                                                                  self._create_misp_attribute('email-src',
                                                                                              'test@domain.com',
                                                                                              INDICATOR_TIMESTAMP))
        cyjax_get_one_mock.assert_not_called()

    def test_save_file_hash_md5_indicator(self, pymisp_mock):
        self._test_save_indicator(pymisp_mock, 'FileHash-MD5', 'md5', '098f6bcd4621d373cade4e832627b4f6')

    def test_save_file_hash_sha1_indicator(self, pymisp_mock):
        self._test_save_indicator(pymisp_mock, 'FileHash-SHA1', 'sha1', 'a94a8fe5ccb19ba61c4c0873d391e987982fbbd3')

    def test_save_file_hash_sha256_indicator(self, pymisp_mock):
        self._test_save_indicator(pymisp_mock, 'FileHash-SHA256', 'sha256', '9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08')

    def test_save_file_hash_ssdeep_indicator(self, pymisp_mock):
        self._test_save_indicator(pymisp_mock, 'FileHash-SSDEEP', 'ssdeep', '96:s4Ud1Lj96tHHlZDrwciQmA+4uy1I0G4HYuL8N3TzS8QsO/wqWXLcMSx:sF1LjEtHHlZDrJzrhuyZvHYm8tKp/RWO')

    def test_save_ipv4_indicator(self, pymisp_mock):
        self._test_save_indicator(pymisp_mock, 'IPv4', 'ip-src', '10.1.1.1')

    def test_save_ipv6_indicator(self, pymisp_mock):
        self._test_save_indicator(pymisp_mock, 'IPv6', 'ip-src', '::1')

    def test_save_url_indicator(self, pymisp_mock):
        self._test_save_indicator(pymisp_mock, 'URL', 'url', 'http://test.com')

    def test_save_hostname_indicator(self, pymisp_mock):
        self._test_save_indicator(pymisp_mock, 'Hostname', 'hostname', 'foobar.test.com')

    def test_save_domain_indicator(self, pymisp_mock):
        self._test_save_indicator(pymisp_mock, 'Domain', 'domain', 'test.com')

    @patch('cyjax.IncidentReport.one', return_value=MockedIncidentReport())
    def test_save_indicator_with_new_url_format(self, cyjax_get_one_mock, pymisp_mock):
        self.client = Client('http://localhost:8888', 'test-misp-key', 'https://cymon.com/incident/report/2334')
        pymisp_mock.return_value.search.return_value = []
        self.client.save_indicator(self._create_indicator('Email', 'test@domain.com'))

        pymisp_mock.return_value.add_event.assert_called_with(
            self._create_misp_event(EVENT_UUID, 'This is a test',
                                    INDICATOR_TIMESTAMP, published=False))
        pymisp_mock.return_value.add_attribute.assert_called_with(AnyClass(str),
                                                                  self._create_misp_attribute('email-src',
                                                                                              'test@domain.com',
                                                                                              INDICATOR_TIMESTAMP))

        cyjax_get_one_mock.assert_called_once_with(2334)

    @patch('cyjax.IncidentReport.one', return_value=MockedIncidentReport(
        techniques=[
            "Malicious File",
            "Process Injection"
        ],
        technique_ids=[
            "T1003.008",
            "T1540"
        ],
        software=[
            "Agent.btz"
        ],
        software_ids=[
            "S0154"
        ]
    ))
    def test_save_indicator_with_mitre_attack_tags(self, cyjax_get_one_mock, pymisp_mock):
        self.client = Client('http://localhost:8888', 'test-misp-key', 'https://cymon.com/incident/report/2334')
        pymisp_mock.return_value.search.return_value = []
        self.client.save_indicator(self._create_indicator('Email', 'test@domain.com'))

        expected_misp_event = self._create_misp_event(EVENT_UUID, 'This is a test', INDICATOR_TIMESTAMP, published=False)
        expected_misp_event.add_tag('test')
        pymisp_mock.return_value.add_event.assert_called_with(expected_misp_event)
        pymisp_mock.return_value.add_attribute.assert_called_with(AnyClass(str),
                                                                  self._create_misp_attribute('email-src',
                                                                                              'test@domain.com',
                                                                                              INDICATOR_TIMESTAMP))

        cyjax_get_one_mock.assert_called_once_with(2334)

    def _test_save_indicator(self, pymisp_mock, indicator_type, misp_indicator_type, indicator_value):
        self.client = Client('http://localhost:8888', 'test-misp-key')
        pymisp_mock.return_value.search.return_value = [{'Event': {'uuid': EVENT_UUID}}]

        self.client.save_indicator(self._create_indicator(indicator_type, indicator_value))

        pymisp_mock.return_value.add_event.assert_not_called()
        pymisp_mock.return_value.add_attribute.assert_called_with(EVENT_UUID,
                                                                  self._create_misp_attribute(misp_indicator_type,
                                                                                              indicator_value,
                                                                                              INDICATOR_TIMESTAMP))

    def test_publish_events_empty_events(self, pymisp_mock):
        """Test publish_events when no events have been added"""
        self.client = Client('http://localhost:8888', 'test-misp-key')
        self.client.added_events = {}
        
        published_count = self.client.publish_events()
        
        self.assertEqual(published_count, 0)
        pymisp_mock.return_value.get_event.assert_not_called()
        pymisp_mock.return_value.publish.assert_not_called()

    def test_publish_events_all_already_published_dict_response(self, pymisp_mock):
        """Test publish_events when all events are already published (dict response)"""
        self.client = Client('http://localhost:8888', 'test-misp-key')
        self.client.added_events = {'source1': 'event-uuid-1', 'source2': 'event-uuid-2'}
        
        # Mock get_event to return dict with published=True
        pymisp_mock.return_value.get_event.side_effect = [
            {'published': True, 'uuid': 'event-uuid-1'},
            {'published': True, 'uuid': 'event-uuid-2'}
        ]
        
        published_count = self.client.publish_events()
        
        self.assertEqual(published_count, 0)
        self.assertEqual(pymisp_mock.return_value.get_event.call_count, 2)
        pymisp_mock.return_value.publish.assert_not_called()

    def test_publish_events_all_already_published_object_response(self, pymisp_mock):
        """Test publish_events when all events are already published (object response)"""
        self.client = Client('http://localhost:8888', 'test-misp-key')
        self.client.added_events = {'source1': 'event-uuid-1', 'source2': 'event-uuid-2'}
        
        # Mock get_event to return objects with published=True
        mock_event1 = MagicMock()
        mock_event1.published = True
        mock_event1.uuid = 'event-uuid-1'
        
        mock_event2 = MagicMock()
        mock_event2.published = True
        mock_event2.uuid = 'event-uuid-2'
        
        pymisp_mock.return_value.get_event.side_effect = [mock_event1, mock_event2]
        
        published_count = self.client.publish_events()
        
        self.assertEqual(published_count, 0)
        self.assertEqual(pymisp_mock.return_value.get_event.call_count, 2)
        pymisp_mock.return_value.publish.assert_not_called()

    def test_publish_events_all_unpublished(self, pymisp_mock):
        """Test publish_events when all events are unpublished"""
        self.client = Client('http://localhost:8888', 'test-misp-key')
        self.client.added_events = {'source1': 'event-uuid-1', 'source2': 'event-uuid-2'}
        
        # Mock get_event to return dict with published=False
        pymisp_mock.return_value.get_event.side_effect = [
            {'published': False, 'uuid': 'event-uuid-1'},
            {'published': False, 'uuid': 'event-uuid-2'}
        ]
        
        published_count = self.client.publish_events()
        
        self.assertEqual(published_count, 2)
        self.assertEqual(pymisp_mock.return_value.get_event.call_count, 2)
        self.assertEqual(pymisp_mock.return_value.publish.call_count, 2)
        pymisp_mock.return_value.publish.assert_any_call({'published': False, 'uuid': 'event-uuid-1'})
        pymisp_mock.return_value.publish.assert_any_call({'published': False, 'uuid': 'event-uuid-2'})

    def test_publish_events_mixed_published_unpublished(self, pymisp_mock):
        """Test publish_events with mix of published and unpublished events"""
        self.client = Client('http://localhost:8888', 'test-misp-key')
        self.client.added_events = {'source1': 'event-uuid-1', 'source2': 'event-uuid-2', 'source3': 'event-uuid-3'}
        
        # Mock get_event to return mix of published and unpublished
        pymisp_mock.return_value.get_event.side_effect = [
            {'published': True, 'uuid': 'event-uuid-1'},   # Already published
            {'published': False, 'uuid': 'event-uuid-2'},  # Not published
            {'published': False, 'uuid': 'event-uuid-3'}   # Not published
        ]
        
        published_count = self.client.publish_events()
        
        self.assertEqual(published_count, 2)
        self.assertEqual(pymisp_mock.return_value.get_event.call_count, 3)
        self.assertEqual(pymisp_mock.return_value.publish.call_count, 2)
        pymisp_mock.return_value.publish.assert_any_call({'published': False, 'uuid': 'event-uuid-2'})
        pymisp_mock.return_value.publish.assert_any_call({'published': False, 'uuid': 'event-uuid-3'})

    def test_publish_events_with_api_error(self, pymisp_mock):
        """Test publish_events when MISP API calls fail"""
        self.client = Client('http://localhost:8888', 'test-misp-key')
        self.client.added_events = {'source1': 'event-uuid-1', 'source2': 'event-uuid-2'}
        
        # Mock get_event to raise exception for first call, succeed for second
        pymisp_mock.return_value.get_event.side_effect = [
            pymisp.PyMISPError("API Error"),
            {'published': False, 'uuid': 'event-uuid-2'}
        ]
        
        published_count = self.client.publish_events()
        
        self.assertEqual(published_count, 1)
        self.assertEqual(pymisp_mock.return_value.get_event.call_count, 2)
        self.assertEqual(pymisp_mock.return_value.publish.call_count, 1)
        pymisp_mock.return_value.publish.assert_called_with({'published': False, 'uuid': 'event-uuid-2'})

    def test_publish_events_with_publish_error(self, pymisp_mock):
        """Test publish_events when publish call fails"""
        self.client = Client('http://localhost:8888', 'test-misp-key')
        self.client.added_events = {'source1': 'event-uuid-1', 'source2': 'event-uuid-2'}
        
        # Mock get_event to succeed, but publish to fail for first event
        pymisp_mock.return_value.get_event.side_effect = [
            {'published': False, 'uuid': 'event-uuid-1'},
            {'published': False, 'uuid': 'event-uuid-2'}
        ]
        pymisp_mock.return_value.publish.side_effect = [
            pymisp.PyMISPError("Publish Error"),
            None  # Second publish succeeds
        ]
        
        published_count = self.client.publish_events()
        
        self.assertEqual(published_count, 1)
        self.assertEqual(pymisp_mock.return_value.get_event.call_count, 2)
        self.assertEqual(pymisp_mock.return_value.publish.call_count, 2)

    def test_publish_events_dict_response_without_published_key(self, pymisp_mock):
        """Test publish_events when dict response doesn't have published key"""
        self.client = Client('http://localhost:8888', 'test-misp-key')
        self.client.added_events = {'source1': 'event-uuid-1'}
        
        # Mock get_event to return dict without published key (should default to False)
        pymisp_mock.return_value.get_event.return_value = {'uuid': 'event-uuid-1'}
        
        published_count = self.client.publish_events()
        
        self.assertEqual(published_count, 1)
        pymisp_mock.return_value.get_event.assert_called_once_with('event-uuid-1')
        pymisp_mock.return_value.publish.assert_called_once_with({'uuid': 'event-uuid-1'})

    def test_publish_events_object_response_without_published_attribute(self, pymisp_mock):
        """Test publish_events when object response doesn't have published attribute"""
        self.client = Client('http://localhost:8888', 'test-misp-key')
        self.client.added_events = {'source1': 'event-uuid-1'}
        
        # Mock get_event to return object without published attribute
        mock_event = MagicMock()
        # Remove the published attribute from the mock
        del mock_event.published
        mock_event.uuid = 'event-uuid-1'
        pymisp_mock.return_value.get_event.return_value = mock_event
        
        published_count = self.client.publish_events()
        
        self.assertEqual(published_count, 1)
        pymisp_mock.return_value.get_event.assert_called_once_with('event-uuid-1')
        pymisp_mock.return_value.publish.assert_called_once_with(mock_event)
