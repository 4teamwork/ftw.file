from ftw.upgrade import UpgradeStep
from ftw.file.config import IS_PLONE_5


class ReimplementDragNDropFeature(UpgradeStep):
    """Reimplement drag n drop feature.
    """

    def __call__(self):
        if IS_PLONE_5:
            self.install_upgrade_profile(['plone.app.registry', 'repositorytool'])
        else:
            self.install_upgrade_profile(['cssregistry', 'jsregistry', 'repositorytool'])
