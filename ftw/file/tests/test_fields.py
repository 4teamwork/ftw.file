from ftw.builder import Builder
from ftw.builder import create
from ftw.file.testing import FTW_FILE_FUNCTIONAL_TESTING
from ftw.testbrowser import browsing
from PIL import Image
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.rfc822.interfaces import IPrimaryFieldInfo
from StringIO import StringIO
from unittest import TestCase


class TestFieldFunctions(TestCase):

    layer = FTW_FILE_FUNCTIONAL_TESTING

    def setUp(self):
        setRoles(self.layer['portal'], TEST_USER_ID, ['Manager'])
        self.file = create(Builder('file').attach_asset(u"testimage.jpg"))
        self.primary_info = IPrimaryFieldInfo(self.file)
        # self.file.getPrimaryField().createScales(self.file)

    def test_available_sizes(self):
        expected = set(['mini', 'thumb', 'large',
                        'listing', 'tile', 'preview', 'icon'])

        sizes = set(
            self.file.restrictedTraverse('@@images').getAvailableSizes())
        self.assertTrue(expected.issubset(sizes),
                        "The available sizes don't include default scales.")

    @browsing
    def test_traversion(self, browser):
        page = browser.login().visit(self.file, view="@@images/file/mini")
        image = Image.open(StringIO(page.contents))
        self.assertEqual((200, 164), image.size)
