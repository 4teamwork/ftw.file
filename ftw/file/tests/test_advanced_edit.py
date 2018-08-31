from ftw.builder import Builder, create
from ftw.file.tests import FunctionalTestCase
from ftw.testbrowser import browsing
import transaction


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

    @browsing
    def test_edit_date_fields(self, browser):
        self.grant('Contributor')
        file = create(Builder('file'))

        # By default, a user having the role "Contributor" does not have the permission
        # to edit the date fields.
        browser.login().open(file, view='edit')
        fieldsets = browser.css('fieldset')
        self.assertEqual(len(fieldsets), 0, "We found some fieldsets although we did not expect any.")

        # Grant the permission and make sure that the user is now able to edit the
        # date fields.
        file.manage_permission('ftw.file: Edit date fields', roles=['Contributor'], acquire=False)
        transaction.commit()
        browser.login().open(file, view='edit')
        fieldsets = browser.css('fieldset')
        self.assertEqual(
            ['Default', 'Dates'],
            fieldsets.css('legend').text
        )
