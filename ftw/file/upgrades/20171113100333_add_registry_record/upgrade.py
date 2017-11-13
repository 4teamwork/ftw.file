from ftw.upgrade import UpgradeStep


class AddRegistryRecord(UpgradeStep):
    """Add registry record (disable download redirect).
    """

    def __call__(self):
        self.install_upgrade_profile()
