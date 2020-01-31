from ftw.builder.session import BuilderSession
from ftw.builder.testing import BUILDER_LAYER
from ftw.builder.testing import set_builder_session_factory
from ftw.testing.layer import COMPONENT_REGISTRY_ISOLATION
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2
from zope.configuration import xmlconfig
import ftw.file.tests.builders  # noqa


def functional_session_factory():
    sess = BuilderSession()
    sess.auto_commit = True
    return sess


class FtwFileLayer(PloneSandboxLayer):

    defaultBases = (z2.ZSERVER_FIXTURE, COMPONENT_REGISTRY_ISOLATION, BUILDER_LAYER)

    def setUpZope(self, app, configurationContext):
        xmlconfig.string(
            '<configure xmlns="http://namespaces.zope.org/zope">'
            '  <include package="z3c.autoinclude" file="meta.zcml" />'
            '  <includePlugins package="plone" />'
            '  <includePluginsOverrides package="plone" />'
            '</configure>',
            context=configurationContext)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'plone.app.imaging:default')
        applyProfile(portal, 'plone.app.registry:default')
        applyProfile(portal, 'plone.app.versioningbehavior:default')
        applyProfile(portal, 'ftw.file:default')


FTW_FILE_FIXTURE = FtwFileLayer()
FTW_FILE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(FTW_FILE_FIXTURE, ), name="ftw.file:Integration")

FTW_FILE_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FTW_FILE_FIXTURE,
           set_builder_session_factory(functional_session_factory)),
    name="ftw.file:Functional")
