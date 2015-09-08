from DateTime import DateTime
from ftw.upgrade import ProgressLogger
from ftw.upgrade import UpgradeStep
from zope.annotation import IAnnotations


ANN_KEY = 'ftw.file-upgrade-1500-migrated-data'


class AddDocumentDateIndex(UpgradeStep):

    def __call__(self):
        self.setup_install_profile('profile-ftw.file.upgrades:1500')
        if not self.catalog_has_index('documentDate'):
            self.catalog_add_index('documentDate', 'DateIndex')
        self.migrate_dates()
        self.catalog_reindex_objects({'portal_type': 'File'},
                                     idxs=['effective', 'documentDate'])

    def migrate_dates(self):
        objects = self.catalog_unrestricted_search({'portal_type': 'File'},
                                                   full_objects=True)

        with ProgressLogger('Migrate file dates', objects) as step:
            for obj in objects:
                ann = IAnnotations(obj)
                if ann.get(ANN_KEY, None) is not None:
                    step()
                    continue

                ann[ANN_KEY] = True

                newdate = obj.getEffectiveDate()
                if not newdate:
                    newdate = obj.created()
                obj.setDocumentDate(newdate)
                obj.setEffectiveDate(DateTime())
                step()
