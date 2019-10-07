from ftw.upgrade import UpgradeStep
from ftw.upgrade.migration import InplaceMigrator
from Products.CMFEditions.interfaces import IVersioned
from Products.CMFEditions.utilities import dereference
from zope.interface import alsoProvides


class MigrateToDexterity(UpgradeStep):
    """Migrate to Dexterity.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.setup_install_profile('profile-plone.app.relationfield:default')
        self.migrate()


    def migrate(self):

        migrator = InplaceMigrator(
            new_portal_type='ftw.file.File',
            ignore_fields=('excludeFromNav'),
            field_mapping={
                'documentDate': 'document_date',
                'originFilename': 'filename_override',
                'isProtected': 'is_protected'
            },
        )

        for obj in self.objects({'portal_type': 'File'},
                                'Migrate ftw.file Files to dexterity'):
            new = migrator.migrate_object(obj)
