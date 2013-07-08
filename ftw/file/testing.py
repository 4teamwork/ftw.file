from ftw.builder.session import BuilderSession
from ftw.builder.testing import BUILDER_LAYER
from ftw.builder.testing import set_builder_session_factory
from ftw.testing import FunctionalSplinterTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.testing.z2 import installProduct
from zope.configuration import xmlconfig


def functional_session_factory():
    sess = BuilderSession()
    sess.auto_commit = True
    return sess


class FtwFileLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, BUILDER_LAYER)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import ftw.file
        xmlconfig.file(
            'configure.zcml', ftw.file, context=configurationContext)
        installProduct(app, 'ftw.file')

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        applyProfile(portal, 'plone.app.registry:default')
        applyProfile(portal, 'ftw.file:default')

FTW_FILE_FIXTURE = FtwFileLayer()
FTW_FILE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(FTW_FILE_FIXTURE, ), name="ftw.file:Integration")

FTW_FILE_FUNCTIONAL_TESTING = FunctionalSplinterTesting(
    bases=(FTW_FILE_FIXTURE,
           set_builder_session_factory(functional_session_factory)),
    name="ftw.file:Functional")
