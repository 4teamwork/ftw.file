from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.ATContentTypes.content.file import ATFile, ATFileSchema
from Products.Archetypes import atapi
from Products.CMFCore.permissions import  View, ModifyPortalContent
from Products.CMFCore.utils import getToolByName
from Products.validation import V_REQUIRED
from ZODB.POSException import ConflictError
from ftw.calendarwidget.browser.widgets import FtwCalendarWidget
from ftw.file import fileMessageFactory as _
from ftw.file.config import PROJECTNAME
from ftw.file.fields import FileField
from ftw.file.interfaces import IFile
from ftw.file.utils import redirect_to_download_by_default
from ftw.journal.interfaces import IWorkflowHistoryJournalizable
from logging import getLogger
from plone.app.blob.field import BlobMarshaller
from zope.interface import implements
from Products.Archetypes.BaseContent import BaseContent
from Products.ATContentTypes.config import ICONMAP
from urllib import quote
from Products.MimetypesRegistry.common import MimeTypeException
import logging

FileSchema = ATFileSchema.copy() + atapi.Schema((
    FileField(
        'file',
        required=True,
        primary=True,
        searchable=True,
        languageIndependent=True,
        index_method='getIndexValue',
        storage=atapi.AnnotationStorage(migrate=True),
        validators=(('isNonEmptyFile', V_REQUIRED),
                    ('checkFileMaxSize', V_REQUIRED)),
        widget=atapi.FileWidget(
            description='',
            label=_(u'label_file', default=u'File'),
            show_content_type=False,
        ),
    ),

     atapi.DateTimeField(
        'documentDate',
        required=False,
        default_method=DateTime,
        widget=FtwCalendarWidget(
            label=_(u'label_document_date', default=u'Document Date'),
            description=_(u'help_document_date', default=u'')),
)))

# Register BlobMarshaller for the marshall layer so it gets
# used when de-marshalling files that are saved with the
# ExternalEditor / WebDav PUT
# This fixes https://extranet.4teamwork.ch/intranet/10-interne-projekte/
# 4teamwork-egov/tracker-4teamwork-egov/465
FileSchema.registerLayer('marshall', BlobMarshaller())

FileSchema['documentDate'].widget.show_hm = False
# clean up schemata, means: set manage portal as write permission
schematas = ['categorization', 'dates', 'ownership', 'settings', 'creators']
for f in FileSchema.keys():
    field_ = FileSchema[f]
    if field_.schemata in schematas:
        field_.write_permission = 'ftw.file: Edit advanced fields'


class File(ATFile):
    """A file content type based on blobs.
    """
    implements(IFile, IWorkflowHistoryJournalizable)

    meta_type = "FtwFile"
    schema = FileSchema
    security = ClassSecurityInfo()

    security.declareProtected(View, 'index_html')
    def index_html(self, REQUEST, RESPONSE):
        """ Redirect to the default view or download view """

        if redirect_to_download_by_default(self):
            return RESPONSE.redirect(self.absolute_url() + '/download')
        else:
            return RESPONSE.redirect(self.absolute_url() + "/view")

    security.declareProtected(View, 'download')
    def download(self, REQUEST=None, RESPONSE=None):
        """Download the file (use default index_html)
        """
        return self.restrictedTraverse('@@download')()

    security.declarePrivate('getIndexValue')
    def getIndexValue(self, mimetype='text/plain'):
        """ an accessor method used for indexing the field's value
            XXX: the implementation is mostly based on archetype's
            `FileField.getIndexable` and rather naive as all data gets
            loaded into memory if a suitable transform was found.
            this should probably use `plone.transforms` in the future """
        field = self.getPrimaryField()
        source = field.getContentType(self)
        transforms = getToolByName(self, 'portal_transforms')

        if transforms._findPath(source, mimetype) is None:
            return ''
        value = str(field.get(self))
        filename = field.getFilename(self)
        try:
            return str(transforms.convertTo(mimetype, value,
                mimetype=source, filename=filename))
        except (ConflictError, KeyboardInterrupt):
            raise
        except:
            getLogger(__name__).exception('exception while trying to convert '
               'blob contents to "text/plain" for %r', self)

    def setFilename(self, value, **kw):
        field = self.getField('file')
        field.getUnwrapped(self).filename = value
    security.declareProtected(ModifyPortalContent, 'setFilename')

    security.declarePublic('getIcon')
    def getIcon(self, relative_to_portal=0):
        """Calculate the icon using the mime type of the file
        """

        field = self.getField('file')
        if not field or not self.get_size():
            # field is empty
            return BaseContent.getIcon(self, relative_to_portal)

        contenttype = field.getContentType(self)
        contenttype_major = contenttype and contenttype.split('/')[0] or ''

        mtr = getToolByName(self, 'mimetypes_registry', None)
        utool = getToolByName(self, 'portal_url')

        mimetypeitem = None
        try:
            mimetypeitem = mtr.lookup(contenttype)
        except MimeTypeException, msg:
            LOG = logging.getLogger('ATCT')
            LOG.error('MimeTypeException for %s. Error is: %s' % (self.absolute_url(), str(msg)))
        if not mimetypeitem:
            icon = None
        else:
            icon = mimetypeitem[0].icon_path

        if not icon:
            if contenttype in ICONMAP:
                icon = quote(ICONMAP[contenttype])
            elif contenttype_major in ICONMAP:
                icon = quote(ICONMAP[contenttype_major])
            else:
                return BaseContent.getIcon(self, relative_to_portal)


        if relative_to_portal:
            return icon
        else:
            # Relative to REQUEST['BASEPATH1']
            res = utool(relative=1) + '/' + icon
            while res[:1] == '/':
                res = res[1:]
            return res

atapi.registerType(File, PROJECTNAME)
