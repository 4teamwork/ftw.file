from ftw.builder import Builder
from ftw.builder import create
from ftw.file.testing import FTW_FILE_FUNCTIONAL_TESTING
from ftw.testbrowser import browsing
from operator import itemgetter
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from unittest import TestCase
import transaction


class TestPagination(TestCase):
    layer = FTW_FILE_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.layer['portal'], TEST_USER_ID, ['Contributor'])

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
            browser.fill({'Title': str(i),
                          'Change Note': str(i)}).save()

        self.assertEqual(
            ['Comment', '11', '10', '9', '8', '7', '6', '5', '4', '3', '2'],
            map(itemgetter(3), browser.css('table.contentHistory').first.lists()))

    @browsing
    def test_pagination_is_disabled_without_history(self, browser):
        browser.login().open(self.file)
        self.assertNotIn(
            'error while rendering plone.belowcontentbody.inlinecontenthistory',
            browser.contents,
            'Pagination should not fail if there is no history.')
