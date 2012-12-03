from ftw.upgrade import UpgradeStep


class ChangePortalPropertiesInstallMissing(UpgradeStep):

    def __call__(self):
        self.setup_install_profile(
            'profile-ftw.file.upgrades:1511')

        self.setup_install_profile(
            'profile-ftw.calendarwidget:default')
