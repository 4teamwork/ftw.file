import unittest2 as unittest
import doctest
from plone.testing import layered
from ftw.file.testing import FTW_FILE_INTEGRATION_TESTING


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(doctest.DocFileSuite('file.txt'),
                layer=FTW_FILE_INTEGRATION_TESTING),
    ])
    return suite
