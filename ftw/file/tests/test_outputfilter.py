from unittest2 import TestCase
from ftw.builder import create
from ftw.builder import Builder
from ftw.file.testing import FTW_FILE_FUNCTIONAL_TESTING
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from ftw.testbrowser import browsing
from zope.annotation.interfaces import IAnnotations
import os


class TestOutputfilter(TestCase):

    layer = FTW_FILE_FUNCTIONAL_TESTING

    def setUp(self):
        setRoles(self.layer['portal'], TEST_USER_ID, ['Manager'])

        self.obj = create(Builder('file').attach_file_containing(
                          self.asset('transparent.gif'), 'transparent.gif'))

    @browsing
    def test_outputfilter_scaled(self, browser):
        page = browser.login().visit(self.obj)
        annos = IAnnotations(self.obj)
        scales = annos.items()[1][1].keys()
        for scale in scales:
            if isinstance(scale, str):
                scale_uid = scale
        image = page.css('.fileListing img')[1].node
        self.assertEqual("http://nohost/plone/file/@@images/" + scale_uid + ".jpeg",
                         image.attrib['src'])

    def asset(self, filename):
        path = os.path.join(os.path.dirname(__file__),
                            'assets',
                            filename)
        with open(path, 'r') as fh:
            return fh.read()
