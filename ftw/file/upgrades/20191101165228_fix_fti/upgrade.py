from ftw.upgrade import UpgradeStep


class FixFTI(UpgradeStep):
    """Fix FTI.
    """

    def __call__(self):
        self.install_upgrade_profile()
