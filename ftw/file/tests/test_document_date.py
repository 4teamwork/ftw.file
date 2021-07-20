from datetime import datetime
from ftw.file.testing import FTW_FILE_FUNCTIONAL_TESTING
from ftw.testing import freeze
from plone import api
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from unittest import TestCase


class TestDocumentDate(TestCase):

    layer = FTW_FILE_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_document_date_gets_set_upon_programmatic_creation(self):
        with freeze(datetime(2015, 2, 22, 1, 0, 0)) as clock:
            file_ = api.content.create(
                title=u'test file',
                container=self.portal,
                type='ftw.file.File')

        # Hint document_date returns the current date if not set.
        self.assertNotEqual(
            file_.document_date,
            datetime.now().date(),
            'document_date has not been set')
