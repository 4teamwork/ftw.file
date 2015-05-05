from ftw.upgrade import UpgradeStep


class EnableTinyMCEImageUpload(UpgradeStep):
    """Enable tiny mce image upload.
    """

    def __call__(self):
        self.install_upgrade_profile()
