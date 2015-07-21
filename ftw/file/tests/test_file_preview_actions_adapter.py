from ftw.builder import Builder
from ftw.builder import create
from ftw.file.interfaces import IFilePreviewActions
from ftw.file.testing import FTW_FILE_FUNCTIONAL_TESTING
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from unittest2 import TestCase


class TestFilePreviewActionsAdapter(TestCase):

    layer = FTW_FILE_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.dummyfile = create(Builder('file').with_dummy_content())

    def test_get_actions_without_actions_to_list(self):
        actions = IFilePreviewActions(self.dummyfile)
        actions.actions_to_list = []

        self.assertEqual(
            [], actions(),
            'If no actions are defined in the actions_to_list-variable '
            'it should return an empty list')

    def test_get_actions_with_not_existing_actions(self):
        actions = IFilePreviewActions(self.dummyfile)
        actions.actions_to_list = ['not-existing']

        self.assertEqual([], actions())

    def test_do_not_add_action_to_actions_list_if_it_returns_none(self):
        actions = IFilePreviewActions(self.dummyfile)
        actions.actions_to_list = ['testaction']
        actions._action_testaction = lambda: {}

        self.assertEqual([], actions())

    def test_actions_method_needs_prefix(self):
        actions = IFilePreviewActions(self.dummyfile)
        actions.actions_to_list = ['testaction']

        actions.testaction = lambda: {'chuck': 'norris'}
        self.assertEqual([], actions())

        actions._action_testaction = lambda: {'chuck': 'norris'}
        self.assertEqual([{'chuck': 'norris'}], actions())

    def test_add_action_to_actions_list(self):
        actions = IFilePreviewActions(self.dummyfile)
        actions.actions_to_list = ['testaction']
        actions._action_testaction = lambda: {'chuck': 'norris'}

        self.assertEqual(
            [{'chuck': 'norris'}], actions())

    def test_sorting_is_like_defined_in_actions_to_list(self):
        actions = IFilePreviewActions(self.dummyfile)
        actions.actions_to_list = ['test1', 'test3', 'test2']
        actions._action_test1 = lambda: {'url': 'test1'}
        actions._action_test2 = lambda: {'url': 'test2'}
        actions._action_test3 = lambda: {'url': 'test3'}

        self.assertEqual([
            {'url': 'test1'}, {'url': 'test3'}, {'url': 'test2'}], actions(),
            'The actions should be sorted like defined in the actions_to_list '
            'variable')


class TestDownloadOriginalAction(TestCase):

    layer = FTW_FILE_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.dummyfile = create(Builder('file').with_dummy_content())

    def test_download_original_action_url_is_correct(self):
        actions = IFilePreviewActions(self.dummyfile)
        action = actions._action_download_original()

        self.assertEqual(
            'http://nohost/plone/file/download', action.get('url'))


class TestOpenPdfAction(TestCase):

    layer = FTW_FILE_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.dummyfile = create(Builder('file').with_dummy_content())

    def test_do_not_display_action_if_document_is_already_a_pdf(self):
        dummyfile = create(Builder('file').attach_file_containing(
            'File content', name='filename.pdf'))
        actions = IFilePreviewActions(dummyfile)
        action = actions._action_open_pdf()

        self.assertEqual({}, action)

    def test_do_not_display_action_if_mimetype_is_not_supported(self):
        dummyfile = create(Builder('file').attach_file_containing(
            'File content', name='filename.bad-mimetype'))
        actions = IFilePreviewActions(dummyfile)
        action = actions._action_open_pdf()

        self.assertEqual({}, action)

    def test_if_the_mimetype_is_supported_it_will_create_an_action(self):
        dummyfile = create(Builder('file').attach_file_containing(
            'File content', name='filename.doc'))
        actions = IFilePreviewActions(dummyfile)
        action = actions._action_open_pdf()

        self.assertIsNotNone(action.get('url', None))


class TestDeleteAction(TestCase):

    layer = FTW_FILE_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.dummyfile = create(Builder('file').with_dummy_content())

    def test_delete_action_url_is_correct(self):
        actions = IFilePreviewActions(self.dummyfile)
        action = actions._action_delete()

        self.assertEqual(
            'http://nohost/plone/file/delete_confirmation', action.get('url'))

    def test_do_not_show_action_if_user_has_no_delete_permission(self):
        logout()
        actions = IFilePreviewActions(self.dummyfile)
        action = actions._action_delete()

        self.assertEqual({}, action)


class TestEditAction(TestCase):

    layer = FTW_FILE_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.dummyfile = create(Builder('file').with_dummy_content())

    def test_edit_action_url_is_correct(self):
        actions = IFilePreviewActions(self.dummyfile)
        action = actions._action_edit()

        self.assertEqual('http://nohost/plone/file/edit', action.get('url'))

    def test_do_not_show_action_if_user_has_no_edit_permission(self):
        logout()
        actions = IFilePreviewActions(self.dummyfile)
        action = actions._action_edit()

        self.assertEqual({}, action)
