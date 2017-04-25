from ftw.upgrade import UpgradeStep


class AddOptionToProtectFilesFromDeletion(UpgradeStep):
    """Add option to protect files from deletion.
    """

    def __call__(self):
        self.install_upgrade_profile()
