from Products.CMFPlone.utils import safe_unicode
from ftw.file import _
from ftw.file.content.dxfile import BlobImageValueType
from plone import api
from zExceptions import BadRequest
from zope.i18n import translate
from zope.publisher.browser import BrowserView
import json


class FileUpload(BrowserView):
    """View for handling drag-and-drop file replace"""

    def __call__(self):
        self.file = self.request.get('file')
        if not self.file:
            raise BadRequest('No content provided.')

        old_filename = safe_unicode(self.context.file.filename)
        new_filename = safe_unicode(self.file.filename)

        change_note = translate(
            _(u'File "{}" replaced with "{}" via drag & drop.'.format(
                old_filename,
                new_filename,
            )))

        repository = api.portal.get_tool('portal_repository')
        repository.save(obj=self.context, comment=change_note, metadata={'filename': old_filename})

        self.filename = new_filename
        self.file.seek(0)
        self.context.file = BlobImageValueType(data=self.file.read(),
                                               filename=self.filename)
        return json.dumps({'success': True})
