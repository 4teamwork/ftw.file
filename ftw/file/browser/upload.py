import json

from plone import api
from Products.CMFCore.utils import getToolByName
from zExceptions import BadRequest
from zope.event import notify
from zope.i18n import translate
from Products.Archetypes.event import ObjectEditedEvent
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

        notify(ObjectEditedEvent(self.context))
        return json.dumps({'success': True})
