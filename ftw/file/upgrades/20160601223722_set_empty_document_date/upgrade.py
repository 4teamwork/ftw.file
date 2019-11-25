from ftw.upgrade import UpgradeStep


class SetEmptyDocumentDate(UpgradeStep):
    """Set empty document date.
    """

    def __call__(self):
        self.install_upgrade_profile()
        query = {'object_provides': 'ftw.file.interfaces.IFile'}
        for obj in self.objects(query, 'Update empty documentDate'):

            if obj.Schema()['documentDate'].get(obj):
                # We skip files with a documentdate
                continue

            obj.Schema()['documentDate'].set(obj, obj.created())
            obj.reindexObject(idxs=['documentDate'])
