from plone.mocktestcase import MockTestCase
from ftw.file.browser.file_view import FileView


class TestFtwFileFunctions(MockTestCase):
    """ Tests for file_view.py
    """

    def setUp(self):

        # Context
        context = self.create_dummy()
        self.mock_context = self.mocker.proxy(context, spec=None, count=False)

        # Request
        self.request = self.create_dummy()

        # Fileview
        self.file_view = FileView(self.mock_context, self.request)

    def test_is_image_allowed(self):
        """ Test for an allowed image
        """
        mock_file = self.mocker.mock(count=False)
        self.expect(mock_file.getContentType()).result('jpeg')
        self.expect(self.mock_context.getFile()).result(mock_file)

        self.replay()

        self.assertTrue(self.file_view.is_image())

    def test_is_image_disallowed(self):
        """ Test for a disallowed image
        """
        mock_file = self.mocker.mock(count=False)
        self.expect(mock_file.getContentType()).result('dwg')
        self.expect(self.mock_context.getFile()).result(mock_file)

        self.replay()

        self.assertTrue(not self.file_view.is_image())
