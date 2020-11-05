from ftw.upgrade import UpgradeStep


class AddInvalidMimetypesRegistryEntry(UpgradeStep):
    """Add invalid_mimetypes registry entry.
    """

    def __call__(self):
        self.install_upgrade_profile()
