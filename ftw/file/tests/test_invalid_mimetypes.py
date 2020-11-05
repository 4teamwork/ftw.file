from ftw.builder import create, Builder
from ftw.file.tests import FunctionalTestCase
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


class TestInvalidMimeTypes(FunctionalTestCase):

    def setUp(self):
        super(TestInvalidMimeTypes, self).setUp()
        self.grant('Manager')

        self.registry = getUtility(IRegistry)

    def test_do_not_create_files_with_invalid_mimetype(self):
        obj = create(Builder('file')
                     .titled(u'Some title')
                     .attach_asset(u'test.pdf'))

        self.assertIn(obj.getId(), self.portal)

        self.registry['ftw.file.filesettings.invalid_mimeteypes'] = [u'application/pdf', ]
        with self.assertRaises(ValueError):
            create(Builder('file')
                   .titled(u'Some title')
                   .attach_asset(u'test.pdf'))
