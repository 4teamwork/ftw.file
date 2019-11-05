from ftw.builder import create, Builder
from ftw.file.tests import FunctionalTestCase
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages


class TestProtectedFiles(FunctionalTestCase):

    def setUp(self):
        super(TestProtectedFiles, self).setUp()
        self.grant('Manager')

    @browsing
    def test_protected_file_cannot_be_deleted(self, browser):
        file = create(Builder('file').titled(u'My Image').attach_asset(u'testimage.jpg'))

        # Plone 5 renders a JSON error page if the request doesn't contain an
        # Accept header with 'text/html', but we want the regular error page.
        browser.replace_request_header('Accept', 'text/html')
        browser.login()

        # Mark the file as protected.
        browser.visit(file, view='edit')
        browser.fill({'Protected': True})
        browser.find_button_by_label('Save').click()

        # Click the "delete" action
        browser.find('Delete').click()

        # Submit the confirmation form.
        with browser.expect_http_error():
            browser.find('Delete').click()
        self.assertEqual(
            ['You are not allowed to delete the file "My Image".'],
            statusmessages.error_messages()
        )
