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
        self.enable_versioning()
        self.migrate()

    def enable_versioning(self):
        repository_tool = self.getToolByName('portal_repository')
        repository_tool.setVersionableContentTypes('ftw.file.File')
        repository_tool.addPolicyForContentType('ftw.file.File',
                                                'version_on_revert')

    def migrate_versions(self, old, new, migrator):

        # Migrate versions
        repositiory = self.getToolByName('portal_repository')
        storage = self.getToolByName('portal_historiesstorage')

        old_obj, old_id = dereference(old, None, self.portal)
        new_obj, new_id = dereference(new, None, self.portal)

        # Move history uid to new object
        # history_uid_handler = self.getToolByName('portal_historyidhandler')
        # old_history_uid = history_uid_handler.queryUid(old_obj)
        # history_uid_handler._setUid(new_obj, old_history_uid)

        # move current version_id/location_id to new obejct
        # new_obj.version_id = old_obj.version_id
        # new_obj.location_id = old_obj.location_id

        # mark as versioned
        # alsoProvides(new_obj, IVersioned)

        # Migrate clones in history storage
        old_history = storage.getHistory(old_id)
        # repo = storage._getZVCRepo()
        # zvc_histid, zvc_selector = \
        #     storage._getZVCAccessInfo(old_history_uid, selector, countPurged)

        for versiondata in old_history:
            old_version_obj = versiondata.object.object
            new_version_obj = migrator.construct_clone_for(old_version_obj)
            migrator.migrate_id_and_uuid(old_version_obj, new_version_obj)
            migrator.migrate_attributes(old_version_obj, new_version_obj)

            new_version_obj.__of__(new.aq_parent)

            # repositiory._recursiveSave(new_version_obj, {},
            #                            versiondata.metadata['sys_metadata'],
            #                            repositiory.autoapply)

            # new_version_obj.__of__(old_version_obj.aq_parent)
            # versiondata.object.object = new_version_obj

    def migrate(self):

        migrator = InplaceMigrator(
            new_portal_type='ftw.file.File',
            ignore_fields=('originFilename', 'excludeFromNav'),
            field_mapping={'documentDate': 'document_date'},
        )

        for obj in self.objects({'portal_type': 'File'},
                                'Migrate ftw.file Files to dexterity'):
            new = migrator.migrate_object(obj)
            self.migrate_versions(obj, new, migrator)
