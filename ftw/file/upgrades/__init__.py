from ftw.upgrade.migration import InplaceMigrator
from zope.annotation.interfaces import IAnnotations
import pkg_resources


try:
    pkg_resources.get_distribution('ftw.solr')
except pkg_resources.DistributionNotFound:
    HAS_FTW_SOLR = False
else:
    HAS_FTW_SOLR = True


try:
    pkg_resources.get_distribution('ftw.topics')
except pkg_resources.DistributionNotFound:
    HAS_FTW_TOPICS = False
else:
    HAS_FTW_TOPICS = True

try:
    pkg_resources.get_distribution('Products.ATContentTypes')
except pkg_resources.DistributionNotFound:
    HAS_AT_CT = False
else:
    HAS_AT_CT = True


def migrate_last_modifier(old_object, new_object):
    value = getattr(old_object, 'lastModifier', None)
    if value:
        IAnnotations(new_object)['collective.lastmodifier'] = value


def add_behaviors_to_file(portal, new_behaviors):
    fti = portal.portal_types.get('ftw.file.File')
    behaviors = set(fti.behaviors)
    behaviors.update(set(new_behaviors))
    fti.behaviors = tuple(behaviors)


class ATToDXMixin(object):

    def install_ftw_file_dx_migration(self, ignore_fields=()):
        self.setup_install_profile('profile-plone.app.relationfield:default')
        self.activate_solr_behavior()
        self.activate_topics_behavior()
        self.migrate(ignore_fields)

    def activate_solr_behavior(self):
        if HAS_FTW_SOLR:
            add_behaviors_to_file(
                self.portal,
                ['ftw.solr.behaviors.IShowInSearch', 'ftw.solr.behaviors.ISearchwords'])

    def activate_topics_behavior(self):
        if HAS_FTW_TOPICS and HAS_AT_CT:

            from ftw.topics.interfaces import ITopicSupport
            from Products.ATContentTypes.content.file import ATFile

            if ITopicSupport.providedBy(ATFile):
                add_behaviors_to_file(
                    self.portal,
                    ['ftw.topics.behavior.ITopicSupportSchema', ])

    def migrate(self, ignore_fields=()):

        migrator = InplaceMigrator(
            new_portal_type='ftw.file.File',
            ignore_fields=(
                ignore_fields + (
                    'excludeFromNav',
                    'lastModifier',
                    'topics',
                    'height',  # flowplayer
                    'width',  # flowplayer
            )),
            field_mapping={
                'documentDate': 'document_date',
                'originFilename': 'filename_override',
                'isProtected': 'is_protected'
            },
            additional_steps=(migrate_last_modifier, )
        )

        for obj in self.objects({'portal_type': 'File'},
                                'Migrate ftw.file Files to dexterity'):
            migrator.migrate_object(obj)
