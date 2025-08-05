"""This module provides the client for MISP API."""

import logging
from datetime import datetime
from typing import Dict, Union
from uuid import uuid4
import urllib3

import cyjax
import pymisp
from pymisp import MISPEvent, MISPAttribute, MISPOrganisation

log = logging.getLogger('cyjax-misp')

misp_org = MISPOrganisation()
misp_org.from_dict(name='Cyjax Ltd.', uuid='acefa06d-2b02-4b7c-994b-0125f87269af')


class MispException(Exception):
    """Exception for MISP errors."""


indicator_map = {
    'FileHash-MD5': 'md5',
    'FileHash-SHA1': 'sha1',
    'FileHash-SHA256': 'sha256',
    'FileHash-SSDEEP': 'ssdeep',
    'IPv4': 'ip-src',
    'IPv6': 'ip-src',
    'URL': 'url',
    'Hostname': 'hostname',
    'Domain': 'domain',
    'Email': 'email-src'
}


class Client:  # pylint: disable=too-few-public-methods disable=E1136
    """MISP client to add indicators."""

    def __init__(self, misp_url: str, misp_key: str, ssl: bool = True, debug: bool = False):
        if debug:
            # Silent logs from pymisp
            logging.getLogger('pymisp').setLevel(logging.DEBUG)
        if not ssl:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.added_events: Dict[str, str] = {}
        try:
            self.misp = pymisp.PyMISP(misp_url, misp_key, ssl=ssl)
        except pymisp.PyMISPError as misp_error:
            raise MispException(
                'Unable to connect to MISP. Please make sure the URL and the API key are correct.') from misp_error

    def save_indicator(self, indicator: dict):
        """
        Saves an indicator.
        :param indicator: The indicator.
        """
        # Check if there is source
        if indicator['source']:
            if '?id=' in indicator['source']:
                # old format link
                source_id = indicator['source'].split('?id=')[1]
            else:
                # new format link
                source_id = indicator['source'].split('/')[-1]
        else:
            # Generate random source uuid
            source_id = str(uuid4())

        misp_event_uuid = self.added_events[
            source_id] if source_id in self.added_events else self._add_event_from_indicator(indicator, source_id)

        attribute = MISPAttribute()
        indicator_type = self._map_indicator_type_to_misp(indicator['type'])
        if indicator_type is None:
            log.error('Unsupported indicator type %s', indicator['type'])
            return

        attribute.from_dict(value=indicator['value'], type=self._map_indicator_type_to_misp(indicator['type']),
                            timestamp=datetime.strptime(indicator['discovered_at'], '%Y-%m-%dT%H:%M:%S%z'))
        self.misp.add_attribute(misp_event_uuid, attribute)

    def publish_events(self) -> int:
        """
        Publishes all last added MISP events.
        """
        published_events = 0
        for event_uuid in self.added_events.values():
            try:
                misp_event = self.misp.get_event(event_uuid)

                if isinstance(misp_event, dict):
                    is_published = misp_event.get('published', False)
                else:
                    is_published = getattr(misp_event, 'published', False)

                if is_published:
                    log.debug('Event "%s" already published', event_uuid)
                    continue

                log.debug('Publishing event "%s"', event_uuid)
                self.misp.publish(misp_event)
                published_events += 1
            except pymisp.PyMISPError as misp_error:
                log.error('Unable to publish event %s: %s', event_uuid, misp_error)
                continue
        return published_events

    def _search_event_by_uuid(self, event_uuid: str) -> Union[str, None]:
        """
        Searches a MISP event by UUID.
        :param event_uuid: The UUID.
        :return: The event UUID if found.
        """
        found_event = self.misp.get_event(event_uuid)
        # Event not found
        if 'errors' in found_event and found_event['errors'][0] == 404:
            return None
        return found_event.uuid

    def _search_event_by_title(self, title: str) -> Union[str, None]:
        """
        Searches a MISP event by title.
        :param title: The title.
        :return: The event UUID if found.
        """
        found_events = self.misp.search(controller='events', eventinfo=title, limit=1)

        if len(found_events) == 0 or 'Event' not in found_events[0]:
            return None

        return found_events[0]['Event']['uuid']

    def _add_event_from_indicator(self, indicator: Dict, source_id: str) -> str:
        """
        Creates a new MISP event for the given indicator.
        :param indicator: The indicator.
        :param source_id: The source ID.
        :return: The event UUID.
        """
        # Check if the event exists
        if 'source_uuid' in indicator:  # Search by UUID
            event_uuid = self._search_event_by_uuid(indicator['source_id'])
        else:  # Search by title
            event_uuid = self._search_event_by_title(indicator['description'])

        # Event not found so add it
        if not event_uuid:
            event_uuid = str(uuid4())
            log.info('Adding new event "%s"', indicator['description'])
            misp_event = MISPEvent()
            misp_event.uuid = event_uuid
            misp_event.Orgc = misp_org

            misp_event.from_dict(info=indicator['description'],
                                 date=indicator['discovered_at'],
                                 analysis=2)

            if 'handling_condition' in indicator:
                misp_event.add_tag("tlp:{}".format(indicator['handling_condition'].lower()))

            # get mitre-attack linked to this indicator source (incident report)
            try:
                incident_report = cyjax.IncidentReport().one(int(source_id))
            except cyjax.exceptions.ForbiddenException:
                # this API key does not have access to incident report resource
                incident_report = None

            if incident_report:
                # mitre techniques
                if incident_report.get('techniques'):
                    for i, technique_name in enumerate(incident_report.get('techniques')):
                        technique_id = incident_report.get('technique_ids')[i]
                        misp_event.add_tag('misp-galaxy:mitre-attack-pattern="{} - {}"'.format(technique_name,
                                                                                               technique_id))

                # mitre software
                if incident_report.get('software'):
                    for i, software_name in enumerate(incident_report.get('software')):
                        software_id = incident_report.get('software_ids')[i]
                        misp_event.add_tag('misp-galaxy:mitre-malware="{} - {}"'.format(software_name, software_id))

            self.misp.add_event(misp_event)

        # Cache the event UUID
        self.added_events[source_id] = event_uuid
        return self.added_events[source_id]

    @staticmethod
    def _map_indicator_type_to_misp(indicator_type: str) -> Union[str, None]:
        """
        Maps a Cyjax indicator type to MISP indicator type.
        :param indicator_type: The indicator type.
        :return: The MISP indicator type.
        """
        return indicator_map[indicator_type] if indicator_type in indicator_map else None
