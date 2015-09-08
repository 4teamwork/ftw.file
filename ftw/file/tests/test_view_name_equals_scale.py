from ftw.builder import Builder
from ftw.builder import create
from ftw.file.testing import FTW_FILE_FUNCTIONAL_TESTING
from ftw.testbrowser import browsing
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from Products.Archetypes.interfaces.base import IBaseObject
from Products.Five import BrowserView
from unittest2 import TestCase
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class TestView(BrowserView):

    def __call__(self):
        return "Success"


class TestViewnameEqualsScale(TestCase):

    layer = FTW_FILE_FUNCTIONAL_TESTING

    def setUp(self):
        gsm = self.layer['portal'].getSiteManager()
        setRoles(self.layer['portal'], TEST_USER_ID, ['Manager'])

        gsm.registerAdapter(TestView,
                            (IBaseObject,IDefaultBrowserLayer),
                            Interface,
                            name="test_mini")
        self.file = create(Builder('file').attach_asset("transparent.gif"))

    @browsing
    def test_view_success(self, browser):
        page = browser.login().visit(self.file, view="test_mini")
        self.assertEquals("Success", page.contents)
