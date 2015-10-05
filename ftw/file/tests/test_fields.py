from ftw.builder import create
from ftw.builder import Builder
from ftw.file.testing import FTW_FILE_FUNCTIONAL_TESTING
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from unittest2 import TestCase
from ftw.testbrowser import browsing
from StringIO import StringIO
from PIL import Image


class TestFieldFunctions(TestCase):

    layer = FTW_FILE_FUNCTIONAL_TESTING

    def setUp(self):
        setRoles(self.layer['portal'], TEST_USER_ID, ['Manager'])
        self.file = create(Builder('file').attach_asset("testimage.jpg"))
        self.file.getPrimaryField().createScales(self.file)

    def test_available_sizes(self):
        expected = set(['mini', 'thumb', 'large',
                       'listing', 'tile', 'preview', 'icon'])
        sizes = self.file.getPrimaryField().getAvailableSizes(self.file).keys()
        sizes = set(sizes)
        self.assertTrue(expected.issubset(sizes),
                        "The available sizes don't include default scales.")

    def test_get_size(self):
        size = self.file.getPrimaryField().getSize(self.file, 'mini')
        self.assertEqual((200, 164), size, "Scale Sizes didn't match")

        size = self.file.getPrimaryField().getSize(self.file, 'preview')
        self.assertEqual((400, 328), size, "Scale Sizes didn't match")

    def test_get_scale(self):
        scale = self.file.getPrimaryField().getScale(self.file, 'mini')
        self.assertEqual('file_mini', scale.__name__)
        self.assertEqual(200, scale.width)
        self.assertEqual(164, scale.height)

    @browsing
    def test_traversion(self, browser):
        page = browser.login().visit(self.file, view="@@images/file/mini")
        image = Image.open(StringIO(page.contents))
        self.assertEqual((200, 164), image.size)

    @browsing
    def test__other_traversion(self, browser):
        page = browser.login().visit(self.file, view="file_mini")
        image = Image.open(StringIO(page.contents))
        self.assertEqual((200, 164), image.size)

    @browsing
    def test_traversion_equality(self, browser):
        page = browser.login().visit(self.file, view="file_mini")
        page2 = browser.login().visit(self.file, view="@@images/file/mini")
        self.assertEqual(page.contents,
                         page2.contents,
                         "The Two Image traversel methods aren't equal")
