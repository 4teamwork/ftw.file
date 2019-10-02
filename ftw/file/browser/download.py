from ftw.file.events.events import FileDownloadedEvent
from ftw.file.utils import redirect_to_download_by_default
from plone import api
from plone.app.blob.download import handleIfModifiedSince  # Also in plone 5
from plone.app.blob.download import handleRequestRange  # Also in plone 5
from plone.app.blob.iterators import BlobStreamIterator
from plone.namedfile.browser import Download as NameFileDownload
from plone.registry.interfaces import IRegistry
from plone.rfc822.interfaces import IPrimaryFieldInfo
from Products.Five.browser import BrowserView
from webdav.common import rfc1123_date
from zope.component import getUtility
from zope.event import notify
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
import urllib


def get_optimized_filename(filename):
    if isinstance(filename, unicode):
        filename = filename.encode('utf-8')

    # We will use the filename in the url and having a percent sign
    # (even a quoted one) in the url seems to cause problems with
    # apache mod_rewrite and look-ahead variables. Thus remove it.
    filename = filename.replace('%', '')
    filename = urllib.quote(filename)

    return filename


@implementer(IPublishTraverse)
class Download(NameFileDownload):

    def __call__(self):

        if self.request.environ.get('PATH_INFO', '').endswith(self.__name__):
            # Redirect to self with fieldname and filename in path
            # This is important for SEO and readability of the url.
            info = IPrimaryFieldInfo(self.context)
            fieldname = info.field.__name__
            filename = get_optimized_filename(info.value.filename)

            current_url = self.context.absolute_url() + '/@@download'
            return self.request.response.redirect(
                '/'.join([current_url, fieldname, filename]))

        file = self._getFile()
        self.set_headers(file)

        request_range = handleRequestRange(
            self.context,
            file.getSize(),
            self.request,
            self.request.response)

        if handleIfModifiedSince(self.context,
                                 self.request,
                                 self.request.response):
            return ''

        # Notify file downloads, but do not notify range requests
        if not ('start' in request_range and request_range['start'] > 0):
            if not api.user.is_anonymous():
                registry = getUtility(IRegistry)
                user_ids = registry['ftw.file.filesettings.user_ids']

                userid = api.user.get_current().getId()
                if userid and userid not in user_ids:
                    notify(FileDownloadedEvent(self.context, self.filename))

        return BlobStreamIterator(self.context.file._blob, **request_range)

    def set_headers(self, file_):
        super(Download, self).set_headers(file_)

        # Additional headers
        self.request.response.setHeader('Last-Modified',
                                        rfc1123_date(self.context._p_mtime))
        self.request.response.setHeader('Accept-Ranges', 'bytes')


class FileViewRedirector(BrowserView):

    def __call__(self):
        response = self.request.RESPONSE
        current_url = self.context.absolute_url()
        filename = self.context.file.filename
        if redirect_to_download_by_default(self.context):
            return response.redirect(
                current_url + '/@@download/file/' + filename)
        else:
            return response.redirect(current_url + "/view")
