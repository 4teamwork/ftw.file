from ftw.upgrade import UpgradeStep


class AddRolemapForNewPermission(UpgradeStep):

    def __call__(self):
        self.setup_install_profile(
            'profile-ftw.file.upgrades:1512')
