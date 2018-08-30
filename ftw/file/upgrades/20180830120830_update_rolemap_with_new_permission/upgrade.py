from ftw.upgrade import UpgradeStep


class UpdateRolemapWithNewPermission(UpgradeStep):
    """Update rolemap with new permission (ftw.file: Edit date fields).
    """

    def __call__(self):
        self.install_upgrade_profile()
