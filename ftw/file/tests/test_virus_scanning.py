from collective.clamav.interfaces import IAVScannerSettings
from collective.clamav.testing import EICAR
from ftw.builder import create
from ftw.builder import Builder
from ftw.file.testing import FTW_FILE_AV_FUNCTIONAL_TESTING
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.registry.interfaces import IRegistry
from unittest import TestCase
from zope.component import getUtility

import transaction


class TestFileVirusScanning(TestCase):

    layer = FTW_FILE_AV_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        registry = getUtility(IRegistry)
        registry.forInterface(IAVScannerSettings).clamav_enabled = False
        transaction.commit()
        self.context = create(Builder('file').attach_file_containing(
                              EICAR, 'v1.txt'), processForm=False)
        registry.forInterface(IAVScannerSettings).clamav_enabled = True
        transaction.commit()

    @browsing
    def test_prevent_download_of_virus_file(self, browser):
        """
        Test we prevent the download of a file with virus (unless virus scanning is explicitly off)
        """
        browser.login().visit(self.context, view='@@download')
        statusmessages.assert_message(
            'Download blocked. The malware Eicar-Test-Signature has been found in the file.'
        )

