from ftw.builder import Builder
from ftw.builder import create
from ftw.file.testing import FTW_FILE_FUNCTIONAL_TESTING
from ftw.testbrowser import browsing
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from unittest import TestCase
from zope.annotation.interfaces import IAnnotations


class TestOutputfilter(TestCase):

    layer = FTW_FILE_FUNCTIONAL_TESTING

    def setUp(self):
        setRoles(self.layer['portal'], TEST_USER_ID, ['Manager'])

        self.obj = create(Builder('file')
                          .titled(u'Some title')
                          .attach_asset(u'testimage.jpg'))

    @browsing
    def test_outputfilter_scaled(self, browser):
        page = browser.login().visit(self.obj)
        annos = IAnnotations(self.obj)
        scales = annos.items()[1][1].keys()
        for scale in scales:
            if isinstance(scale, str):
                scale_uid = scale

        image = page.css('.fileListing img').first
        url = "{}/testimage.jpg/@@images/".format(self.layer['portal'].absolute_url())
        self.assertEqual(
            url + scale_uid + ".jpeg",
            image.attrib['src'])
