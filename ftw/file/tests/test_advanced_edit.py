from ftw.file.tests import FunctionalTestCase
from ftw.testbrowser import browsing


class TestAdvancedEdit(FunctionalTestCase):

    @browsing
    def test_no_advanced_edit(self, browser):
        self.grant('Contributor', 'Editor')
        browser.login().open(self.portal.absolute_url() + '/createObject?type_name=File')
        browser.css('fieldset')
        fieldsets = browser.css('fieldset')
        self.assertEqual(len(fieldsets), 0, "We found Fieldsets. We didn't expect any'")

    @browsing
    def test_advanced_edit(self, browser):
        self.grant('Reviewer')
        browser.login().open(self.portal.absolute_url() + '/createObject?type_name=File')
        fieldsets = browser.css('fieldset')
        self.assertEqual(
            ['Default', 'Categorization', 'Dates', 'Creators', 'Settings'],
            fieldsets.css('legend').text
        )
