import transaction

from ftw.file.testing import FTW_FILE_FUNCTIONAL_TESTING
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.testing import setRoles
from plone.testing.z2 import Browser
from unittest2 import TestCase
from pyquery import PyQuery


class TestAdvancedEdit(TestCase):

    layer = FTW_FILE_FUNCTIONAL_TESTING

    def setUp(self):
        self.browser = Browser(self.layer['app'])
        self.browser.handleErrors = False

        self.portal = self.layer['portal']

        transaction.commit()

    def login(self):
        self.browser.addHeader(
            'Authorization',
            'Basic %s:%s' % (TEST_USER_NAME, TEST_USER_PASSWORD,))

    def test_no_advanced_edit(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor', 'Editor'])
        transaction.commit()
        self.login()
        self.browser.open(self.portal.absolute_url() + '/createObject?type_name=File')
        html = PyQuery(self.browser.contents)
        fieldsets = html('fieldset')
        self.assertEqual(len(fieldsets), 0, "We found Fieldsets. We didn't expect any'")

    def test_advanced_edit(self):
        form_tabs = ["Default",
                     "Categorization",
                     "Dates",
                     "Creators",
                     "Settings",
                     "Ownership"
                     ]
        setRoles(self.portal, TEST_USER_ID, ['Contributor', 'Editor', 'Reviewer'])
        transaction.commit()
        self.login()
        self.browser.open(self.portal.absolute_url() + '/createObject?type_name=File')
        html = PyQuery(self.browser.contents)
        fieldsets = html('fieldset')
        self.assertEqual(len(fieldsets), 5, "We expected 5 Fieldsets got %s" % len(fieldsets))
        legends = fieldsets('legend')
        for legend in legends:
            self.assertIn(legend.text, form_tabs)
