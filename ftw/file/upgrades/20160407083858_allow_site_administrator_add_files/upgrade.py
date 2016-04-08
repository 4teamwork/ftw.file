from ftw.upgrade import UpgradeStep


class AllowSiteAdministratorAddFiles(UpgradeStep):
    """Allow site administrator add files.
    """

    def __call__(self):
        self.install_upgrade_profile()
