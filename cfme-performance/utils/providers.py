from utils.conf import cfme_performance
from utils.log import logger
import json
import requests


def add_provider(provider):
    """Adds Provider via the Rest API."""
    logger.debug('Adding Provider: {}, Type: {}'.format(provider['name'], provider['type']))


def add_providers(providers):
    for provider in providers:
        add_provider(cfme_performance['providers'][provider])


def refresh_provider(provider):
    logger.debug('TODO: Initiate Provider Refresh')


def refresh_provider_host(provider):
    logger.debug('TODO: Initiate Provider Host Refresh')


def refresh_provider_vm(provider):
    logger.debug('TODO: Initiate Provider VM Refresh')
