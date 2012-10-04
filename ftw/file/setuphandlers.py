from Products.CMFCore.utils import getToolByName
from ftw.file.config import INDEXES


def add_indexes(context, logger):
    """Add our indexes to the catalog.

    Doing it here instead of in profiles/default/catalog.xml means we
    do not need to reindex those indexes after every reinstall.
    """

    catalog = getToolByName(context, 'portal_catalog')
    indexes = catalog.indexes()

    for name, meta_type in INDEXES:
        if name not in indexes:
            catalog.addIndex(name, meta_type)
            logger.info('Added index: %s' % name)

def import_various(context):
    """Import step for configuration that is not handled in xml files.
    """
    # Only run step if a flag file is present
    if context.readDataFile('ftw.file.setuphandlers.txt') is None:
        return
    logger = context.getLogger('ftw.file')
    site = context.getSite()
    add_indexes(site, logger)
