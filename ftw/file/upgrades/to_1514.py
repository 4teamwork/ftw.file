from ftw.upgrade import UpgradeStep

class ReindexIcons(UpgradeStep):

    def __call__(self):
        self.catalog_rebuild_index('getIcon')
