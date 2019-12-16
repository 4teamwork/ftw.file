from ftw.file.config import IS_PLONE_5
from ftw.upgrade import UpgradeStep


class Plone5_ProvidePrecompiledBundle(UpgradeStep):
    """Plone 5: Provide precompiled bundle.
    """

    def __call__(self):
        if IS_PLONE_5:
            self.install_upgrade_profile()
