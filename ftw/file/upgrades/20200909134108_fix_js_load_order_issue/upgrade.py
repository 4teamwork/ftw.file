from ftw.upgrade import UpgradeStep


class FixJsLoadOrderIssue(UpgradeStep):
    """Fix js load order issue.
    """

    def __call__(self):
        self.install_upgrade_profile()
