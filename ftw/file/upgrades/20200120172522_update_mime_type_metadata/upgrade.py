from ftw.upgrade import UpgradeStep


class UpdateMimeTypeMetadata(UpgradeStep):
    """Update mime type metadata.
    """

    def __call__(self):
        self.install_upgrade_profile()
        query = {'object_provides': 'ftw.file.interfaces.IFile'}
        for obj in self.objects(query, 'Update mime_type'):
            obj.reindexObject(idxs=['getId'])  # update metadata
