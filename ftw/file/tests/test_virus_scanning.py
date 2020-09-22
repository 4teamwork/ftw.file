from collective.clamav.interfaces import IAVScannerSettings
from collective.clamav.testing import EICAR
from collective.clamav.validator import SCAN_RESULT_KEY
from ftw.builder import create
from ftw.builder import Builder
from ftw.file.testing import FTW_FILE_AV_FUNCTIONAL_TESTING
from ftw.file.testing import FTW_FILE_AV_INTEGRATION_TESTING
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.registry.interfaces import IRegistry
from six import StringIO
from unittest import TestCase
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility

import json
import transaction


class TestFileVirusScanningDownloads(TestCase):

    layer = FTW_FILE_AV_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        # Don't scan files while creating test fixtures
        registry = getUtility(IRegistry)
        registry.forInterface(IAVScannerSettings).clamav_enabled = False
        transaction.commit()
        self.context = create(Builder('file').attach_file_containing(
                              EICAR, 'contaminated.txt'), processForm=False)
        registry.forInterface(IAVScannerSettings).clamav_enabled = True
        transaction.commit()

        # Make sure the above doesn't cache a scan attempt in the request
        # and ruin our test
        annotations = IAnnotations(self.portal.REQUEST)
        if SCAN_RESULT_KEY in annotations:
            del annotations[SCAN_RESULT_KEY]

    @browsing
    def test_prevent_download_of_virus_file(self, browser):
        """
        Test we prevent the download of a file with virus (unless virus scanning is explicitly off)
        """
        browser.login().visit(self.context, view='@@download')
        statusmessages.assert_message(
            'Download blocked. The malware Eicar-Test-Signature has been found in the file.'
        )


class TestVirusScanningUploads(TestCase):

    layer = FTW_FILE_AV_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        # Don't scan files while creating test fixtures
        registry = getUtility(IRegistry)
        registry.forInterface(IAVScannerSettings).clamav_enabled = False
        transaction.commit()
        self.file_ = create(
            Builder('file')
                .titled('Document')
                .attach_file_containing('My PDF', name='test.pdf')
        )
        registry.forInterface(IAVScannerSettings).clamav_enabled = True
        transaction.commit()
        # Make sure the above doesn't cache a scan attempt in the request
        # and ruin our test
        annotations = IAnnotations(self.portal.REQUEST)
        if SCAN_RESULT_KEY in annotations:
            del annotations[SCAN_RESULT_KEY]


    def test_virus_protection_drag_and_drop(self):
        """ Clamav validator should stop updates with a virus infected file """
        dodgy_file = StringIO(EICAR)
        dodgy_file.filename = 'innocent_looking_file.txt'
        dodgy_file.content_type = 'text/plain'
        self.portal.REQUEST.set('file', dodgy_file)

        ajax_upload_view = self.file_.restrictedTraverse('ajax-upload')
        response = json.loads(ajax_upload_view())

        self.assertFalse(response['success'])
        self.assertEqual('Validation failed, file is virus-infected. (Eicar-Test-Signature FOUND)',
                         response['errors'][0]['message'])
