from ftw.file import fileMessageFactory as _
from plone import api
from plone.namedfile.file import NamedBlobImage
from Products.CMFPlone.utils import safe_unicode
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

        self.filename = self.file.filename
        self.file.seek(0)
        self.context.file = NamedBlobImage(data=self.file.read(),
                                           filename=safe_unicode(self.filename))

        change_note = translate(_('File replaced with Drag & Drop.'))
        repository = api.portal.get_tool('portal_repository')
        repository.save(obj=self.context, comment=change_note)

        return json.dumps({'success': True})
