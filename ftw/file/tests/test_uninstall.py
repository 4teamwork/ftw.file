from ftw.testing.genericsetup import apply_generic_setup_layer
from ftw.testing.genericsetup import GenericSetupUninstallMixin
from unittest import TestCase


@apply_generic_setup_layer
class TestGenericSetupUninstall(TestCase, GenericSetupUninstallMixin):

    # All policies for the entry are removed but not the ftw.file.File entry itself
    skip_files = ('repositorytool.xml',)
    package = 'ftw.file'
