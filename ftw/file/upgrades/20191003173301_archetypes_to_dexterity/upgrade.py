from ftw.upgrade import UpgradeStep
import os
from ftw.file.upgrades import ATToDXMixin


class MigrateToDexterity(UpgradeStep, ATToDXMixin):
    """Migrate to Dexterity.
    """

    def __call__(self):
        self.install_upgrade_profile()
        if os.environ.get('FTW_FILE_SKIP_DEXTERITY_MIGRATION', '').lower() == 'true':
            return
        self.install_ftw_file_dx_migration()
