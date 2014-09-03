from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from ftw.calendarwidget.browser.widgets import FtwCalendarWidget
from ftw.file import fileMessageFactory as _
from ftw.file.config import PROJECTNAME
from ftw.file.fields import FileField
from ftw.file.interfaces import IFile
from ftw.file.utils import redirect_to_download_by_default
from ftw.journal.interfaces import IWorkflowHistoryJournalizable
from logging import getLogger
from os import path
from PIL import Image
from plone.app.blob.field import BlobMarshaller
from Products.Archetypes import atapi
from Products.Archetypes.BaseContent import BaseContent
from Products.Archetypes.Widget import StringWidget
from Products.ATContentTypes.config import ICONMAP
from Products.ATContentTypes.content.file import ATFile
from Products.ATContentTypes.content.file import ATFileSchema
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.permissions import View
from Products.CMFCore.utils import getToolByName
from Products.MimetypesRegistry.common import MimeTypeException
from Products.validation import V_REQUIRED
from urllib import quote
from ZODB.POSException import ConflictError
from zope.interface import implements
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
    atapi.StringField(
        name='originFilename',
        required=False,
        widget=StringWidget(
            helper_js=("++resource++hideOriginFilenameField.js", ),
            label=_(u'label_origin_filename', default=u'Filename'),
            description=_(
                u'help_origin_filename',
                default=u"Insert a filename if you want to change the "
                        "original filename. The extension (i.e. .docx) "
                        "will not be modified")
        ),
    ),
    atapi.DateTimeField(
        'documentDate',
        required=False,
        default_method=DateTime,
        widget=FtwCalendarWidget(
            label=_(u'label_document_date', default=u'Document Date'),
            description=_(u'help_document_date', default=u'')
        ),
    ),

))

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
            return str(transforms.convertTo(
                mimetype,
                value,
                mimetype=source,
                filename=filename))
        except (ConflictError, KeyboardInterrupt):
            raise
        except:
            getLogger(__name__).exception(
                'exception while trying to convert '
                'blob contents to "text/plain" for %r', self)

    security.declareProtected(ModifyPortalContent, 'setFilename')
    def setFilename(self, value, **kw):
        field = self.getField('file')
        field.getUnwrapped(self).filename = value

    security.declareProtected(ModifyPortalContent, 'setOriginFilename')
    def setOriginFilename(self, value, **kw):
        """Overrides the filename with the given value.
        It keeps the old extenstion.
        """
        # file_delete contains '' if a file is uploaded, otherwise 'nochange'
        if self.REQUEST.form.get('file_delete', 'nochange') != 'nochange':
            return

        filename = self.getFilename()
        if not value or not filename:
            return

        if isinstance(value, unicode):
            value = value.encode('utf-8')

        self.setFilename('{0}{1}'.format(value, path.splitext(filename)[1]))

    security.declareProtected(ModifyPortalContent, 'getOriginFilename')
    def getOriginFilename(self):
        """Gets the filename without extension
        """
        filename = self.getFilename()
        if not filename:
            return None
        return path.splitext(filename)[0]

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
            LOG.error('MimeTypeException for %s. Error is: %s' % (
                self.absolute_url(), str(msg)))
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

    def is_image(self):
        file_ = self.getFile()
        mimetype = file_.getContentType()
        Image.init()
        open_handlers = Image.OPEN.keys()
        extensions = []
        for key, value in Image.EXTENSION.items():
            if value in open_handlers:
                extensions.append(key.strip('.'))

        mr = getToolByName(self, 'mimetypes_registry')
        mimetypes = mr.lookup(mimetype)
        if not mimetypes:
            return False  # unknown mimetype

        mime_extensions = mimetypes[0].extensions
        for ext in mime_extensions:
            if ext in extensions:
                return True
        for glob in mr.lookup(mimetype)[0].globs:
            if glob.strip("*.") in extensions:
                return True
        return False

atapi.registerType(File, PROJECTNAME)
