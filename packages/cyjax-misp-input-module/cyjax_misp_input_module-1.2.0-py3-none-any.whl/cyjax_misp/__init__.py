"""Module allows to poll indicators of compromise from Cyjax to MISP"""
__author__ = 'Cyjax Ltd.'
__version__ = '1.2.0'
__email__ = 'github@cyjax.com'
__contact__ = 'github@cyjax.com'

import cyjax

cyjax.client_name = 'cyjax-misp-input-module/{}'.format(__version__)
