import json

from Products.CMFCore.utils import getToolByName
from plone import api
from zExceptions import BadRequest
from zope.i18n import translate
from zope.publisher.browser import BrowserView

from ftw.file import fileMessageFactory as _


class FileUpload(BrowserView):
    """View for handling drag-and-drop file replace"""

    def __call__(self):
        self.file = self.request.get('file')
        if not self.file:
            raise BadRequest('No content provided.')

        self.filename = self.file.filename
        self.context.update(file=self.file, originFilename=self.filename)

        portal = api.portal.get()
        repository_tool = getToolByName(portal, 'portal_repository')

        if repository_tool.isVersionable(self.context):
            # TODO: This creates another entry in the history resulting in two consecutive history entries.
            repository_tool.save(
                self.context,
                comment=translate(_('File replaced with Drag & Drop.'),
                                  context=self.request)
            )

        return json.dumps({'success': True})