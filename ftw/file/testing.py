from ftw.builder.session import BuilderSession
from ftw.builder.testing import BUILDER_LAYER
from ftw.builder.testing import set_builder_session_factory
from ftw.testing import FunctionalSplinterTesting
from plone.app.testing import applyProfile
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing.z2 import installProduct
from zope.component import eventtesting
from zope.configuration import xmlconfig
import os


def functional_session_factory():
    sess = BuilderSession()
    sess.auto_commit = True
    return sess


class FtwFileLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, BUILDER_LAYER)

    def setUpZope(self, app, configurationContext):
        xmlconfig.string(
            '<configure xmlns="http://namespaces.zope.org/zope">'
            '  <include package="z3c.autoinclude" file="meta.zcml" />'
            '  <includePlugins package="plone" />'
            '  <includePluginsOverrides package="plone" />'
            '</configure>',
            context=configurationContext)

        installProduct(app, 'ftw.file')

        os.environ['BUMBLEBEE_DEACTIVATE'] = "True"

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        applyProfile(portal, 'plone.app.registry:default')
        applyProfile(portal, 'ftw.file:default')
        eventtesting.setUp()

    def tearDownZope(self, app):
        del os.environ['BUMBLEBEE_DEACTIVATE']

FTW_FILE_FIXTURE = FtwFileLayer()
FTW_FILE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(FTW_FILE_FIXTURE, ), name="ftw.file:Integration")

FTW_FILE_FUNCTIONAL_TESTING = FunctionalSplinterTesting(
    bases=(FTW_FILE_FIXTURE,
           set_builder_session_factory(functional_session_factory)),
    name="ftw.file:Functional")


class FtwFileBumblebeeLayer(FtwFileLayer):

    def setUpZope(self, app, configurationContext):
        super(FtwFileBumblebeeLayer, self).setUpZope(app, configurationContext)
        os.environ['BUMBLEBEE_APP_ID'] = 'local'
        os.environ['BUMBLEBEE_SECRET'] = 'secret'
        os.environ['BUMBLEBEE_URL'] = 'http://bumblebee/api/v1'

    def setUpPloneSite(self, portal):
        super(FtwFileBumblebeeLayer, self).setUpPloneSite(portal)
        applyProfile(portal, 'ftw.file:bumblebee')

    def tearDownZope(self, app):
        super(FtwFileBumblebeeLayer, self).tearDownZope(app)
        del os.environ['BUMBLEBEE_APP_ID']
        del os.environ['BUMBLEBEE_SECRET']
        del os.environ['BUMBLEBEE_URL']


FTW_FILE_BUMBLEBEE_FIXTURE = FtwFileBumblebeeLayer()
FTW_FILE_BUMBLEBEE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(FTW_FILE_BUMBLEBEE_FIXTURE, ),
    name="ftw.file:Integration Bumblebee")

FTW_FILE_BUMBLEBEE_FUNCTIONAL_TESTING = FunctionalSplinterTesting(
    bases=(FTW_FILE_BUMBLEBEE_FIXTURE,
           set_builder_session_factory(functional_session_factory)),
    name="ftw.file:Functional Bumblebee")
