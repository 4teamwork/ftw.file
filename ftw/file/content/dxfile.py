from datetime import datetime

from plone.autoform.directives import write_permission

from ftw.file import _
from ftw.file.interfaces import IFile
from ftw.file.utils import is_image
from ftw.journal.interfaces import IWorkflowHistoryJournalizable
from os import path
from plone.dexterity.content import Item
from plone.namedfile.field import INamedBlobFileField
from plone.namedfile.field import NamedBlobFile
from plone.namedfile.file import NamedBlobImage
from plone.supermodel import model
from plone.supermodel.directives import primary
from Products.CMFCore.utils import getToolByName
from Products.MimetypesRegistry.common import MimeTypeException
from z3c.form import validator
from zope import schema
from zope.component import provideAdapter
from zope.interface import implementer
from zope.interface import implements
from zope.interface import Invalid
import logging

LOGGER = logging.getLogger('ftw.file')


def default_document_date():
    return datetime.now().date()

class BlobImageValueType(NamedBlobImage):

    def __init__(self, data='', contentType='', filename=None):
        """
        Lookup contentType from Plone's more extensive mimetypes registry
        instead of just Python's mimetypes.
        """
        if not contentType:
            mtr = getToolByName(self, 'mimetypes_registry', None)
            mimetypeitem = mtr.lookupExtension(filename)
            if mimetypeitem:
                contentType = mimetypeitem.normalized()

        super(BlobImageValueType, self).__init__(data, contentType, filename)


@implementer(INamedBlobFileField)
class NamedBlobMixedFileImageField(NamedBlobFile):
    """This is a NamedBlobFileField with all the features of
    NamedBlobImageField"""

    _type = BlobImageValueType


class IFileSchema(model.Schema):

    primary('file')
    file = NamedBlobMixedFileImageField(
        title=_(u'label_file', default=u'File'),
        required=True)

    filename_override = schema.TextLine(
        title=_(u'label_filename_override', default=u'Filename'),
        required=False,
        description=_(
            u'help_filename_override',
            default=u"Insert a filename if you want to change the "
            "original filename. The extension (i.e. .docx) "
            "will not be modified. Please do not enter \"/\"."))

    document_date = schema.Date(
        required=True,
        defaultFactory=default_document_date,
        title=_(u'label_document_date', default=u'Document Date'),
    )

    write_permission(is_protected='ftw.file.ProtectFile')
    is_protected = schema.Bool(
        required=False,
        default=False,
        title=_(u'label_is_protected', default=u'Protected'),
        description=_(u'help_is_protected',
                      default=u'The file cannot cannot be deleted if this option is checked.'),
    )


class FilenameValidator(validator.SimpleFieldValidator):
    """Do not allow / in filename"""

    def validate(self, value):
        if value and '/' in value:
            errmsg = _(
                u'filename_override_validator_error',
                default=u'"/" (Slash in filenames is not allowed..'
            )
            raise Invalid(errmsg)


validator.WidgetValidatorDiscriminators(FilenameValidator,
                                        field=IFileSchema['filename_override'])
provideAdapter(FilenameValidator)


# TODO: Implement the js for the dx type
# FileSchema = ATFileSchema.copy() + atapi.Schema((
#     FileField(
#         searchable=True,
#     ),

#     atapi.StringField(
#         validators=('isSafeOriginFilename',),
#         widget=StringWidget(
#             helper_js=(
#               "++resource++ftw.file.resources/hideOriginFilenameField.js", ),


class File(Item):
    # TODO: Move IWorkflowHistoryJournalizable into zcml
    implements(IFile, IWorkflowHistoryJournalizable)

    def _get_filename_override(self):
        filename = self.file.filename
        if not filename:
            return None
        return path.splitext(filename)[0]

    def _set_filename_override(self, value):
        """Overrides the filename with the given value and keep the
        old extension.
        """
        if not value:
            return

        if not isinstance(value, unicode):
            value = value.decode('utf-8')

        filename = self.file.filename

        if not filename:
            return

        self.file.filename = u'{0}{1}'.format(value,
                                              path.splitext(filename)[1])

    filename_override = property(_get_filename_override, _set_filename_override)

    def is_image(self):
        return is_image(self.file.contentType)

    def getIcon(self, relative_to_portal=False):
        """ Calculate the icon using the mime type of the file
            if no file return nothing.
        """
        # if not self.file:
        #     # field is empty
        #     return ''

        # contenttype = self.file.getContentType(self)
        contenttype = self.file.contentType
        #contenttype_major = contenttype and contenttype.split('/')[0] or ''

        mtr = getToolByName(self, 'mimetypes_registry', None)
        utool = getToolByName(self, 'portal_url')

        mimetypeitem = None
        try:
            # import pdb; pdb.set_trace()
            mimetypeitem = mtr.lookup(contenttype)
        except MimeTypeException, msg:
            LOGGER.error('MimeTypeException for %s. Error is: %s' % (
                self.absolute_url(), str(msg)))
        if not mimetypeitem:
            return super(File, self).getIcon(relative_to_portal)

        icon = mimetypeitem[0].icon_path
        if not relative_to_portal:
            utool = getToolByName(self, 'portal_url')
            icon = utool(relative=1) + '/' + icon
            while icon[:1] == '/':
                icon = icon[1:]
        return icon
