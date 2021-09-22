from ftw.file import _
from ftw.file.content.dxfile import BlobImageValueType
from plone import api
from Products.CMFPlone.utils import safe_unicode
from zExceptions import BadRequest
from zope.i18n import translate
from zope.publisher.browser import BrowserView
import json
import ntpath


class FileUpload(BrowserView):
    """View for handling drag-and-drop file replace"""

    def __call__(self):
        self.file = self.request.get('file')
        if not self.file:
            raise BadRequest('No content provided.')

        old_filename = safe_unicode(self.context.file.filename)
        new_filename = safe_unicode(self.file.filename)

        if ntpath.basename(new_filename) != new_filename:
            # Windows Edge uploads files with the filename being the whole
            # Path on the windows system. Get the basename instead.
            new_filename = ntpath.basename(new_filename)

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

        self.context.setModificationDate()  # Updates to current date
        self.context.reindexObject(idxs=['modified'])
        return json.dumps({'success': True})
