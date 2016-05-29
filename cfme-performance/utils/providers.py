from utils.conf import cfme_performance
from utils.log import logger


def add_provider(provider):
    """Adds Provider via the Rest API."""
    logger.debug('Adding Provider: {}, Type: {}'.format(str(provider), provider['type']))


def add_providers(providers):
    for provider in providers:
        add_provider(cfme_performance['providers'][provider])
