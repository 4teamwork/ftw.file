from AccessControl import ClassSecurityInfo
from ftw.file import fileMessageFactory as _
from ftw.file.config import PROJECTNAME
from ftw.file.fields import FileField
from ftw.file.interfaces import IFile
from ftw.journal.interfaces import IWorkflowHistoryJournalizable
from logging import getLogger
from plone.app.blob.field import BlobMarshaller
from Products.Archetypes import atapi
from Products.ATContentTypes.content.file import ATFile, ATFileSchema
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.permissions import View
from Products.CMFCore.utils import getToolByName
from Products.validation import V_REQUIRED
from ZODB.POSException import ConflictError
from zope.interface import implements


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
            show_content_type = False,
        ),
    ),
))

# Register BlobMarshaller for the marshall layer so it gets
# used when de-marshalling files that are saved with the
# ExternalEditor / WebDav PUT
# This fixes https://extranet.4teamwork.ch/intranet/10-interne-projekte/4teamwork-egov/tracker-4teamwork-egov/465
FileSchema.registerLayer('marshall', BlobMarshaller())

# clean up schemata, means: set manage portal as write permission
schematas = ['categorization', 'dates', 'ownership', 'settings']
for f in FileSchema.keys():
    field = FileSchema[f]
    if field.schemata in schematas:
        field.write_permission = ManagePortal

if 'effectiveDate' in FileSchema.keys():
    FileSchema['effectiveDate'].widget.visible = {'view': 'visible',
                                                  'edit': 'visible'}
    FileSchema['effectiveDate'].schemata = 'default'

class File(ATFile):
    """A file content type based on blobs.
    """
    implements(IFile, IWorkflowHistoryJournalizable)

    meta_type = "FtwFile"
    schema = FileSchema
    security = ClassSecurityInfo()

    security.declareProtected(View, 'index_html')

    def index_html(self, REQUEST, RESPONSE):
        """ download the file as an attachment """
        field = self.getPrimaryField()
        return field.download(self, REQUEST, RESPONSE)

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

atapi.registerType(File, PROJECTNAME)
