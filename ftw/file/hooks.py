from ftw.file.config import INDEXES
from Products.CMFCore.utils import getToolByName
import logging


LOGGER = logging.getLogger('ftw.file')


def installed(site):
    add_indexes(site)


def add_indexes(context):
    """Add our indexes to the catalog.

    Doing it here instead of in profiles/default/catalog.xml means we
    do not need to reindex those indexes after every reinstall.
    """

    catalog = getToolByName(context, 'portal_catalog')
    indexes = catalog.indexes()

    for name, meta_type in INDEXES:
        if name not in indexes:
            catalog.addIndex(name, meta_type)
            LOGGER.info('Added index: %s' % name)
