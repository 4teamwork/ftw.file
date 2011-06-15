try:
    from Products.contentmigration.archetypes import InplaceATItemMigrator
    from Products.contentmigration.migrator import BaseInlineMigrator
    haveContentMigrations = True
    BaseMigrator = InplaceATItemMigrator
    InlineMigrator = BaseInlineMigrator
except ImportError:
    BaseMigrator = object
    InlineMigrator = object
    haveContentMigrations = False

from plone.app.blob.migrations import migrate, getMigrationWalker

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


def getFtwFileMigrationWalker(self):
    return getMigrationWalker(self, migrator=FtwFileMigrator)


def migrateFtwFiles(self):
    return migrate(self, walker=getFtwFileMigrationWalker)