from ftw.upgrade import UpgradeStep
from ftw.upgrade.migration import InplaceMigrator


class MigrateToDexterity(UpgradeStep):
    """Migrate to Dexterity.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.setup_install_profile('profile-plone.app.relationfield:default')
        self.enable_versioning()
        self.migrate()

    def enable_versioning(self):
        repository_tool = self.getToolByName('portal_repository')
        repository_tool.setVersionableContentTypes('ftw.file.File')
        repository_tool.addPolicyForContentType('ftw.file.File',
                                                'version_on_revert')

    def migrate(self):

        migrator = InplaceMigrator(
            new_portal_type='ftw.file.File',
            ignore_fields=('originFilename', 'excludeFromNav'),
            field_mapping={'documentDate': 'document_date'},
        )

        for obj in self.objects({'portal_type': 'File'},
                                'Migrate ftw.file Files to dexterity'):
            migrator.migrate_object(obj)
