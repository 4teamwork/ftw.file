from ftw.file.testing import FTW_FILE_FUNCTIONAL_TESTING
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.testing.z2 import Browser
from StringIO import StringIO
from unittest2 import TestCase
import transaction


class TestFileOverlay(TestCase):

    layer = FTW_FILE_FUNCTIONAL_TESTING

    def setUp(self):
        self.browser = Browser(self.layer['app'])
        self.browser.handleErrors = False

        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        self.file_ = StringIO(
                    'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\x00\x00'
                    '\x00!\xf9\x04\x04\x00\x00\x00\x00,\x00\x00\x00\x00\x01'
                    '\x00\x01\x00\x00\x02\x02D\x01\x00;')

        self.portal.invokeFactory('File', 'f1', file=self.file_)
        self.context = self.portal.f1
        transaction.commit()

    def login(self):
        self.browser.addHeader(
            'Authorization',
            'Basic %s:%s' % (TEST_USER_NAME, TEST_USER_PASSWORD,))

    def test_image_displayed(self):
        self.browser.open(self.context.absolute_url() + '/view')
        self.assertIn('<a id="preview" class="colorboxLink"'
                      ' href="http://nohost/plone/f1/@@images/file">',
                      self.browser.contents)
        self.assertIn('<img src="http://nohost/plone/f1/@@images',
                      self.browser.contents)

    def test_image_link_works(self):
        self.browser.open(self.context.absolute_url() + '/@@images/file')
        self.assertEqual('image/gif', self.browser.headers['content-type'])
        self.assertEqual(self.file_.read(), self.browser.contents)
