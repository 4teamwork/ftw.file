from plone.app.blob import field
from zope.event import notify
from webdav.common import rfc1123_date
from ftw.file.events.events import FileDownloadedEvent
from zope.component import getMultiAdapter
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from urllib import quote


class FileField(field.FileField):

    def index_html(self, instance, REQUEST=None, RESPONSE=None,
                   no_output=False, disposition=None):
        """Kicks download.
        Writes data including file name and content type to RESPONSE
        """
        raw_file = self.get(instance, raw=True)
        if not REQUEST:
            REQUEST = instance.REQUEST
        if not RESPONSE:
            RESPONSE = REQUEST.RESPONSE

        RESPONSE.setHeader('Last-Modified', rfc1123_date(instance._p_mtime))
        RESPONSE.setHeader('Content-Type', self.getContentType(instance))
        RESPONSE.setHeader('Accept-Ranges', 'bytes')

        filename = self.getFilename(instance)
        if isinstance(filename, unicode):
            filename = filename.encode('utf8')

        user_agent = REQUEST.get('HTTP_USER_AGENT', '')
        if 'MSIE' in user_agent:
            filename = quote(filename)
            RESPONSE.setHeader("Content-disposition",
                               'attachment; filename=%s' % filename)

        else:
            RESPONSE.setHeader(
                "Content-disposition", 'attachment; filename="%s"' % filename)

        filename = self.getFilename(instance)

        ps = getMultiAdapter(
            (instance, instance.REQUEST),
            name='plone_portal_state')

        if not ps.anonymous():
            registry = getUtility(IRegistry)
            user_ids = registry['ftw.file.filesettings.user_ids']
            if not ps.member().id in user_ids:
                notify(FileDownloadedEvent(instance, filename))

        return raw_file
