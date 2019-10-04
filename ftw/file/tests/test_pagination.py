from ftw.builder import Builder
from ftw.builder import create
from ftw.file.testing import FTW_FILE_FUNCTIONAL_TESTING
from ftw.testbrowser import browsing
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from unittest2 import TestCase
import transaction


class TestPagination(TestCase):
    layer = FTW_FILE_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.layer['portal'], TEST_USER_ID, ['Manager'])

        self.file = create(Builder('file')
                           .titled(u'An important file')
                           .with_dummy_content())

    @browsing
    def test_pagination_is_used(self, browser):
        # enable history
        portal_repository = self.portal.portal_repository
        portal_repository.addPolicyForContentType(u'ftw.file.File',
                                                  u'at_edit_autoversion')
        portal_repository.setVersionableContentTypes(
            portal_repository.getVersionableContentTypes() + [u'ftw.file.File'])
        transaction.commit()

        # make history entrys
        for i in range(12):
            browser.login().open(self.file, view='edit')
            browser.fill({'Title': str(i)}).save()

        self.assertIn("file_download_version?version_id=11",
                      browser.contents,
                      "Revision id 11 is new and should be "
                      "displayed in pagination.")
        self.assertNotIn('file_download_version?version_id=2"',
                         browser.contents,
                         "Revision 0 is old and should be on the second page "
                         " of the pagination view.")

    @browsing
    def test_pagination_is_disabled_without_history(self, browser):
        browser.login().open(self.file)
        self.assertNotIn(
            'error while rendering plone.belowcontentbody.inlinecontenthistory',
            browser.contents,
            'Pagination should not fail if there is no history.')