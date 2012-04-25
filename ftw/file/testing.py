from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from zope.configuration import xmlconfig
from plone.testing.z2 import installProduct


class FtwFileLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import ftw.file
        xmlconfig.file('configure.zcml', ftw.file, context=configurationContext)
        installProduct(app, 'ftw.file')

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        applyProfile(portal, 'plone.app.registry:default')
        applyProfile(portal, 'ftw.file:default')

FTW_FILE_FIXTURE = FtwFileLayer()
FTW_FILE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(FTW_FILE_FIXTURE,), name="ftw.file:Integration")
FTW_FILE_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FTW_FILE_FIXTURE,), name="ftw.file:Functional")
