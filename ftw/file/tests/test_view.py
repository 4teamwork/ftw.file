import transaction

from ftw.file.testing import FTW_FILE_FUNCTIONAL_TESTING
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from Products.CMFCore.utils import getToolByName
from plone.app.testing import setRoles
from plone.testing.z2 import Browser
from unittest2 import TestCase


class TestFileName(TestCase):

    layer = FTW_FILE_FUNCTIONAL_TESTING

    def setUp(self):
        self.browser = Browser(self.layer['app'])
        self.browser.handleErrors = False

        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        self.portal.invokeFactory('File', 'f1')
        self.context = self.portal.f1
        transaction.commit()
        self._set_allowAnonymousViewAbout_property(True)

    def login(self):
        self.browser.addHeader(
            'Authorization',
            'Basic %s:%s' % (TEST_USER_NAME, TEST_USER_PASSWORD,))

    def _set_allowAnonymousViewAbout_property(self, value):
        site_props = getToolByName(self.context, 'portal_properties').site_properties
        site_props._updateProperty('allowAnonymousViewAbout', value)
        transaction.commit()

    def is_author_visible(self):
        self.browser.open(self.context.absolute_url())
        return '<th>Author</th>' in self.browser.contents

    def test_logged_in_user_sees_author_when_allowAnonymousViewAbout(self):
        self.login()
        self.assertTrue(self.is_author_visible(),
                        'Logged in user should see author if allowAnonymousViewAbout is True.')

    def test_logged_in_user_sees_author_when_not_allowAnonymousViewAbout(self):
        self.login()
        self._set_allowAnonymousViewAbout_property(False)
        self.assertTrue(self.is_author_visible(),
                        'Logged in user should see author if allowAnonymousViewAbout is False.')

    def test_anonymous_user_sees_author_when_allowAnonymousViewAbout(self):
        self.assertTrue(self.is_author_visible(),
                        'Anonymous user should see author if allowAnonymousViewAbout is True.')

    def test_anonymous_user_dont_sees_author_when_not_allowAnonymousViewAbout(self):
        self._set_allowAnonymousViewAbout_property(False)
        self.assertFalse(self.is_author_visible(),
                         'Anonymous user should not see author if allowAnonymousViewAbout is False.')
