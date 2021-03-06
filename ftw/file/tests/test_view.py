from ftw.builder import Builder
from ftw.builder import create
from ftw.file.testing import FTW_FILE_FUNCTIONAL_TESTING
from ftw.testbrowser import browsing
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import getFSVersionTuple
from unittest import TestCase
from zope.component import getUtility

import transaction


class TestFileName(TestCase):

    layer = FTW_FILE_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.context = create(Builder('file')
                              .titled(u'Some title')
                              .attach_asset(u"transparent.gif"))
        self._set_allowAnonymousViewAbout_property(True)

    def _set_allowAnonymousViewAbout_property(self, value):
        if getFSVersionTuple() > (5, 0):
            registry = getUtility(IRegistry)
            registry['plone.allow_anon_views_about'] = value
        else:
            site_props = getToolByName(self.context,
                                       'portal_properties').site_properties
            site_props._updateProperty('allowAnonymousViewAbout', value)
        transaction.commit()

    def is_author_visible(self, page):
        return 'Author' in page.css(".fileListing th").text

    @browsing
    def test_logged_in_user_sees_author_when_allowAnonymousViewAbout(self,
                                                                     browser):
        page = browser.login().visit(self.context, view="file_view")
        self.assertTrue(self.is_author_visible(page),
                        'Logged in user should see author if '
                        'allowAnonymousViewAbout is True.')

    @browsing
    def test_logged_in_user_sees_author_when_not_allowAnonymousViewAbout(self, browser):
        self._set_allowAnonymousViewAbout_property(False)
        page = browser.login().visit(self.context, view="file_view")
        self.assertTrue(self.is_author_visible(page),
                        'Logged in user should see author if '
                        'allowAnonymousViewAbout is False.')

    @browsing
    def test_anonymous_user_sees_author_when_allowAnonymousViewAbout(self,
                                                                     browser):
        page = browser.visit(self.context, view="file_view")
        self.assertTrue(self.is_author_visible(page),
                        'Anonymous user should see author if '
                        'allowAnonymousViewAbout is True.')

    @browsing
    def test_anonymous_user_dont_sees_author_when_not_allowAnonymousViewAbout(self, browser):
        self._set_allowAnonymousViewAbout_property(False)
        page = browser.visit(self.context, view="file_view")
        self.assertFalse(self.is_author_visible(page),
                         'Anonymous user should not see author if '
                         'allowAnonymousViewAbout is False.')
