try:
    from Products.contentmigration.archetypes import InplaceATItemMigrator
    from Products.contentmigration.migrator import BaseInlineMigrator
    from Products.contentmigration.walker import CustomQueryWalker
    haveContentMigrations = True
    BaseMigrator = InplaceATItemMigrator
    InlineMigrator = BaseInlineMigrator
except ImportError:
    BaseMigrator = object
    InlineMigrator = object
    haveContentMigrations = False

from plone.app.blob.migrations import migrate
from Products.CMFCore.utils import getToolByName
from Products.contentmigration.catalogpatch import applyCatalogPatch
from Products.contentmigration.catalogpatch import removeCatalogPatch
from Products.contentmigration.common import HAS_LINGUA_PLONE


# # migration of file content to blob content type
class FtwFileMigrator(BaseMigrator):
    src_portal_type = 'ftw_File'
    src_meta_type = 'ftw_File'
    dst_portal_type = 'File'
    dst_meta_type = 'FtwFile'

    # migrate all fields except 'file', which needs special handling...
    fields_map = {
        'file': None,
    }

    def migrate_data(self):
        self.new.getField('file').getMutator(self.new)(self.old)

    def last_migrate_reindex(self):
        self.new.reindexObject(idxs=['object_provides', 'portal_type',
            'Type', 'UID'])


class FtwFileMigrationWalker(CustomQueryWalker):
    """
    """
    def walk(self):
        """Walks around and returns all objects which needs migration

        :return: objects (with acquisition wrapper) that needs migration
        :rtype: generator
        """
        catalog = self.catalog
        query = self.additionalQuery.copy()
        query['portal_type'] = self.src_portal_type
        query['meta_type'] = self.src_meta_type

        if HAS_LINGUA_PLONE and 'Language' in catalog.indexes():
            #query['Language'] = catalog.uniqueValuesFor('Language')
            query['Language'] = 'all'
            
        for brain in catalog(query)[:500]:
            obj = brain.getObject()
            
            if self.callBefore is not None and callable(self.callBefore):
                if self.callBefore(obj, **self.kwargs) == False:
                    continue
            
            try: state = obj._p_changed
            except: state = 0
            if obj is not None:
                yield obj
                # safe my butt
                if state is None: obj._p_deactivate()


def getFtwFileMigrationWalker(context):
    """ set up migration walker """
    portal = getToolByName(context, 'portal_url').getPortalObject()
    return FtwFileMigrationWalker(portal, FtwFileMigrator, transaction_size=100)


def migrateFtwFiles(context):

    portal = getToolByName(context, 'portal_url').getPortalObject()
    out = ''
    try:
        catalog_class = applyCatalogPatch(portal)
        out = migrate(context, walker=getFtwFileMigrationWalker)
    finally:
        removeCatalogPatch(catalog_class)

    return out
