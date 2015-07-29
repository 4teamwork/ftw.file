from ftw.builder import Builder
from ftw.builder import create
from ftw.file.bumblebee.interfaces import IFilePreviewCollectorDefaultLists
from ftw.file.testing import FTW_FILE_BUMBLEBEE_FUNCTIONAL_TESTING
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from unittest2 import TestCase
from zope.component import getMultiAdapter


class TestCollectorDefaultLists(TestCase):

    layer = FTW_FILE_BUMBLEBEE_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.dummyfile = create(Builder('file').with_dummy_content())
        self.view = self.dummyfile.unrestrictedTraverse('@@file_preview')
        self.adapter = getMultiAdapter(
            (self.dummyfile, self.request, self.view),
            IFilePreviewCollectorDefaultLists)

    def test_get_list_if_listname_is_available(self):
        self.adapter._list_my_list = ['chuck', 'norris']

        self.assertEqual(
            ['chuck', 'norris'], self.adapter('my_list'),
            "Only list-variables with prefix _list_ should be returned")

    def test_get_empty_list_if_listname_is_not_available(self):
        self.assertEqual(
            [],
            self.adapter('not_existing_list'))

    def test_get_only_prefixed_lists(self):
        self.adapter.my_list = ['chuck', 'norris']

        self.assertEqual(
            [], self.adapter('my_list'),
            "You need to prefix your list with '_list_' and call the "
            "adapter without prefix")
