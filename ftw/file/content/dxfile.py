from datetime import datetime
from ftw.file import _
from ftw.file.interfaces import IFile
from ftw.file.utils import is_image
from ftw.journal.interfaces import IWorkflowHistoryJournalizable
from os import path
from plone.dexterity.content import Item
from plone.namedfile.field import INamedBlobFileField
from plone.namedfile.field import NamedBlobFile
from plone.namedfile.file import NamedBlobImage as BlobImageValueType
from plone.supermodel import model
from plone.supermodel.directives import primary
from z3c.form import validator
from zope import schema
from zope.component import provideAdapter
from zope.interface import implementer
from zope.interface import implements
from zope.interface import Invalid


def default_document_date():
    return datetime.now().date()


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

    originfilename = schema.TextLine(
        title=_(u'label_origin_filename', default=u'Filename'),
        required=False,
        description=_(
            u'help_origin_filename',
            default=u"Insert a filename if you want to change the "
            "original filename. The extension (i.e. .docx) "
            "will not be modified. Please do not enter \"/\"."))

    document_date = schema.Date(
        required=True,
        defaultFactory=default_document_date,
        title=_(u'label_document_date', default=u'Document Date'),
    )


class FilenameValidator(validator.SimpleFieldValidator):
    """Do not allow / in filename"""

    def validate(self, value):
        if value and '/' in value:
            errmsg = _(
                u'origin_filename_validator_error',
                default=u'"/" (Slash in filenames is not allowed..'
            )
            raise Invalid(errmsg)


validator.WidgetValidatorDiscriminators(FilenameValidator,
                                        field=IFileSchema['originfilename'])
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

    def _get_originfilename(self):
        filename = self.file.filename
        if not filename:
            return None
        return path.splitext(filename)[0]

    def _set_originfilename(self, value):
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

    originfilename = property(_get_originfilename, _set_originfilename)

    def is_image(self):
        return is_image(self.file.contentType)
