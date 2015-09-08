try:
    from Products.contentmigration.archetypes import InplaceATItemMigrator
    from Products.contentmigration.migrator import BaseInlineMigrator
    from Products.contentmigration.walker import CustomQueryWalker
    haveContentMigrations = True
    BaseMigrator = InplaceATItemMigrator
    InlineMigrator = BaseInlineMigrator
except ImportError:
    BaseMigrator = object
    InlineMigrator = object
    haveContentMigrations = False

from plone.app.blob.migrations import migrate
from Products.CMFCore.utils import getToolByName
from Products.contentmigration.catalogpatch import applyCatalogPatch
from Products.contentmigration.catalogpatch import removeCatalogPatch
from Products.contentmigration.common import HAS_LINGUA_PLONE
from Products.contentmigration.archetypes import BaseATMigrator
from zope.app.component.hooks import getSite
from zope.component import getUtility
from Acquisition import aq_inner, aq_base, aq_parent
from zope.component.interfaces import IFactory
from Products.Archetypes.interfaces import IReferenceable
from Products.Archetypes.ArchetypeTool import getType
from Products.Archetypes.config import REFERENCE_ANNOTATION


class FtwFileMigrator(BaseMigrator):
    """ Migration of file content to blob content type
    """
    src_portal_type = 'ftw_File'
    src_meta_type = 'ftw_File'
    dst_portal_type = 'File'
    dst_meta_type = 'FtwFile'

    # migrate all fields except 'file', which needs special handling...
    fields_map = {
        'file': None,
    }

    def migrate_data(self):
        oldfield = self.old.getField('file')
        value = oldfield.get(self.old)
        self.new.getField('file').getMutator(self.new)(value)

    def last_migrate_reindex(self):
        self.new.reindexObject(idxs=['object_provides', 'portal_type',
                                     'Type', 'UID'])
    # XXX: doesn't work yet, trying transmogrifier instead
    # def last_migrate_versions(self):
    #     atool = getToolByName(self.old, 'portal_archivist')
    #     history = atool.getHistory(self.old)
    #     for version in history:
    #         obj = version.data.object
    #         migrator = FtwFileVersionMigrator(obj)
    #         migrator.migrate()


class FtwFileVersionMigrator(BaseATMigrator):
    src_portal_type = 'ftw_File'
    src_meta_type = 'ftw_File'
    dst_portal_type = 'File'
    dst_meta_type = 'FtwFile'

    # migrate all fields except 'file', which needs special handling...
    fields_map = {
        'file': None,
    }

    def __init__(self, obj, src_portal_type=None, dst_portal_type=None,
                 **kwargs):
        self.old = aq_inner(obj)
        self.orig_id = self.old.getId()
        self.old_id = '%s_MIGRATION_' % self.orig_id
        self.new = None
        self.new_id = self.orig_id
        self.parent = aq_parent(self.old)
        if src_portal_type is not None:
            self.src_portal_type = src_portal_type
        if dst_portal_type is not None:
            self.dst_portal_type = dst_portal_type
        self.kwargs = kwargs

        # safe id generation
        while hasattr(aq_base(self.parent), self.old_id):
            self.old_id += 'X'

    def renameOld(self):
        """Renames the old object
        """
        setattr(self.parent, self.old_id, self.old)
        delattr(self.parent, self.orig_id)

    def createNew(self):
        """Create the new object
        """
        portal = getSite()
        typesTool = getToolByName(portal, 'portal_types')
        fti = typesTool.getTypeInfo(self.dst_portal_type)
        factory = getUtility(IFactory, fti.factory)
        obj = factory(self.new_id, **self.schema)
        if hasattr(obj, '_setPortalTypeName'):
            obj._setPortalTypeName(self.getId())
        setattr(self.parent, self.new_id, obj)
        self.new = getattr(aq_inner(self.parent).aq_explicit, self.new_id)

    def remove(self):
        """Removes the old item
        """
        delattr(self.parent, self.old_id)

    def reorder(self):
        """Reorder the new object in its parent"""
        return

    def beforeChange_schema(self):
        """Load the values of fields from according to fields_map if present.
        Each key in fields_map is a field in the old schema and each
        value is a field in the new schema.  If fields_map isn't a
        mapping, each filed in the old schema will be migrated into
        the new schema.  Obeys field modes for readable and writable
        fields.  These values are then passed in as field kwargs into
        the constructor in the createNew method."""

        old_schema = self.old.Schema()

        portal = getSite()
        typesTool = getToolByName(portal, 'portal_types')
        fti = typesTool.getTypeInfo(self.dst_portal_type)
        archetype = getType(self.dst_meta_type, fti.product)
        new_schema = archetype['klass'].schema

        if self.only_fields_map:
            old_field_names = self.fields_map.keys()
        else:
            old_field_names = old_schema.keys()

        # Let the migrator handle the id and dates
        for omit_field_name in ['id', 'creation_date',
                                'modification_date']:
            if omit_field_name in old_field_names:
                old_field_names.remove(omit_field_name)

        kwargs = getattr(self, 'schema', {})
        for old_field_name in old_field_names:
            old_field = self.old.getField(old_field_name)
            new_field_name = self.fields_map.get(old_field_name,
                                                 old_field_name)

            if new_field_name is None:
                continue

            new_field = new_schema.get(new_field_name, None)
            if new_field is None:
                continue

            if ('r' in old_field.mode and 'w' in new_field.mode):
                accessor = (
                    getattr(old_field, self.accessor_getter)(self.old)
                    or old_field.getAccessor(self.old))
                value = accessor()
                kwargs[new_field_name] = value
        self.schema = kwargs

    def migrate_owner(self):
        """Migrates the zope owner
        """
        self.new._owner = self.old.getOwner(info=1)

    def migrate_localroles(self):
        """Migrate local roles
        """
        return

    def migrate_user_roles(self):
        """Migrate roles added by users
        """
        return

    def migrate_at_uuid(self):
        """Migrate AT universal uid
        """
        if not IReferenceable.providedBy(self.old):
            return  # old object doesn't support AT uuids

        uid = self.old.UID()
        self.new._setUID(uid)

    def migrate_references(self):
        """Migrate references annotation."""
        # Restor the references annotation
        if hasattr(self, REFERENCE_ANNOTATION):
            at_references = getattr(self, REFERENCE_ANNOTATION)
            setattr(self.new, REFERENCE_ANNOTATION, at_references)


class FtwFileMigrationWalker(CustomQueryWalker):
    """
    """

    def walk(self):
        """Walks around and returns all objects which needs migration

        :return: objects (with acquisition wrapper) that needs migration
        :rtype: generator
        """
        catalog = self.catalog
        query = self.additionalQuery.copy()
        query['portal_type'] = self.src_portal_type
        query['meta_type'] = self.src_meta_type

        if HAS_LINGUA_PLONE and 'Language' in catalog.indexes():
            query['Language'] = 'all'

        for brain in catalog(query)[:1000]:
            obj = brain.getObject()

            if self.callBefore is not None and callable(self.callBefore):
                if self.callBefore(obj, **self.kwargs) is False:
                    continue

            try:
                state = obj._p_changed
            except:
                state = 0
            if obj is not None:
                yield obj
                # safe my butt
                if state is None:
                    obj._p_deactivate()


def getFtwFileMigrationWalker(context):
    """ set up migration walker """
    portal = getToolByName(context, 'portal_url').getPortalObject()
    return FtwFileMigrationWalker(
        portal, FtwFileMigrator, transaction_size=100)


def migrateFtwFiles(context):

    portal = getToolByName(context, 'portal_url').getPortalObject()
    out = ''
    try:
        catalog_class = applyCatalogPatch(portal)
        out = migrate(context, walker=getFtwFileMigrationWalker)
    finally:
        removeCatalogPatch(catalog_class)

    return out


# version migration using collective.jsonify
import urllib
import urlparse
import logging
import json
import base64
logger = logging.getLogger('ftw.file.migration')


class UrllibrpcException(Exception):
    """Raised when reading an url fails.
    """

    def __init__(self, code, url):
        self.code = code
        self.url = url

    def __str__(self):
        return '%s:%s' % (self.code, self.url)


class Urllibrpc(object):

    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password

    def __getattr__(self, item):

        def callable():
            scheme, netloc, path, params, query, fragment = urlparse.urlparse(
                self.url)
            if '@' not in netloc:
                netloc = '%s:%s@%s' % (self.username, self.password, netloc)
            if path.endswith("/"):
                path = path[:-1]
            path = path + '/' + item
            url = urlparse.urlunparse(
                (scheme, netloc, path, params, query, fragment))
            f = urllib.urlopen(url)
            content = f.read()
            if f.getcode() != 200:
                raise UrllibrpcException(f.getcode(), f.geturl())
            f.close()
            return content
        return callable


def migrate_file_versions(
    context, remote_user='admin', remote_password='admin'):
    """Migrate file version using collective.jsonify as data source.
    """
    remote_url = 'http://127.0.0.1:9080'
    catalog = getToolByName(context, 'portal_catalog')
    repo_tool = getToolByName(context, 'portal_repository')
    files = catalog(portal_type='File')
    for file_ in files:
        url = '%s%s' % (remote_url, file_.getPath())
        remote = Urllibrpc(url, remote_user, remote_password)

        try:
            remote_data = remote.get_item_with_file()
        except UrllibrpcException, e:
            logger.warn("Failed reading url '%s' with error code %s." %
                         (e.url, e.code))
            continue

        try:
            remote_data = json.loads(remote_data)
        except ValueError:
            logger.warn(
                "No JSON object could be decoded using data from url '%s'." %
                url)
            continue

        obj = file_.getObject()
        field = obj.getField('file')
        file_data = to_utf8(remote_data.get('_datafield_file'))

        # a list indicates multiple versions
        if isinstance(file_data, list):
            principals = []
            for version in file_data:
                field.set(obj, base64.b64decode(version.get('data')))
                field.getUnwrapped(obj).filename = version.get('filename')
                field.getUnwrapped(obj).content_type = version.get(
                    'content_type')
                if version.get('version_id') != 'WORKING_COPY':
                    principals.append(
                        version['version_sysmetadata']['principal'])
                    repo_tool._recursiveSave(obj, {},
                                         version.get('version_sysmetadata'),
                                         autoapply=repo_tool.autoapply)
                else:
                    mdate_mutator = obj.getField(
                        'modification_date').getMutator(obj)
                    mdate_mutator(remote_data.get('modification_date'))

            # fix principal in metadata
            hm = repo_tool.getHistoryMetadata(obj)
            for version_id, metadata in hm._full.items():
                if version_id < len(principals):
                    metadata['metadata']['sys_metadata']['principal'] = \
                        principals[version_id]
                    hm._full[version_id] = metadata

        # Do nothing if we didn't get multiple versions


def to_utf8(obj):
    """Recursively convert unicode to uft-8 strings in lists and dicts."""
    if isinstance(obj, unicode):
        obj = obj.encode('utf8')
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            obj[i] = to_utf8(v)
    elif isinstance(obj, dict):
        new_obj = {}
        for k, v in obj.iteritems():
            if isinstance(k, unicode):
                k = k.encode('utf8')
            new_obj[k] = to_utf8(v)
        obj = new_obj
    return obj
