from ftw.builder import Builder
from ftw.builder import create
from ftw.file.tests import FunctionalTestCase
from ftw.testbrowser import browsing
from unittest2 import skipUnless
import pkg_resources


try:
    pkg_resources.require('ftw.activity>=2')
except (pkg_resources.VersionConflict, pkg_resources.DistributionNotFound):
    HAS_ACTIVITY_2 = False
else:
    HAS_ACTIVITY_2 = True
    from ftw.activity.tests.helpers import get_soup_activities


@skipUnless(HAS_ACTIVITY_2, 'ftw.activity 2.0 not installed')
class TestActivity2Downloads(FunctionalTestCase):

    @browsing
    def test_activity_created_when_file_downloaded(self, browser):
        self.grant('Contributor')
        file_ = create(Builder('file').with_dummy_content())
        browser.login().open(file_, view='@@download')

        self.assertIn(
            {'path': '/plone/file',
             'action': 'file:downloaded'},
            get_soup_activities(('path', 'action')))
