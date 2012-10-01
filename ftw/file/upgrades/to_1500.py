from ftw.upgrade import ProgressLogger
from ftw.upgrade import UpgradeStep
from zope.app.component.hooks import getSite
import logging
from Products.CMFCore.utils import getToolByName
from DateTime import DateTime
LOG = logging.getLogger('ftw.file.upgrades')


class AddDocumentDateIndex(UpgradeStep):

    def __call__(self):
        self.setup_install_profile('profile-ftw.file.upgrades:1500')
        self.add_document_index_and_migrate()

    def add_document_index_and_migrate(self):
        site = getSite()
        catalog = getToolByName(site, 'portal_catalog')
        if not self.catalog_has_index('documentDate'):
            self.catalog_add_index('documentDate', 'DateIndex')
        results = catalog.search({'portal_type': 'File'})
        with ProgressLogger('Reindex ftw.files', results) as step:
            for brain in results:
                obj = brain.getObject()
                if not obj.getDocumentDate():
                    newdate = obj.getEffectiveDate()
                    if not newdate:
                        newdate = obj.created()
                    obj.setDocumentDate(newdate)
                    obj.setEffectiveDate(DateTime())
                obj.reindexObject(idxs=['effective', 'documentDate'])
                step()
