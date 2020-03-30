from Products.statusmessages.interfaces import IStatusMessage
from ftw.file.events.events import FileDownloadedEvent
from ftw.file.imaging import ImagingMixin
from ftw.file.interfaces import IFtwFileField
from OFS.Image import File
from PIL.Image import ANTIALIAS
from plone.app.blob.field import FileField as BlobFileField
from plone.app.blob.download import handleIfModifiedSince
from plone.app.blob.download import handleRequestRange
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from urllib import quote
from webdav.common import rfc1123_date
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.event import notify
from zope.interface import implements

from ftw.file import fileMessageFactory as _


class FileField(BlobFileField, ImagingMixin):
    implements(IFtwFileField)

    _properties = BlobFileField._properties.copy()
    _properties.update({
        'pil_quality': 88,
        'pil_resize_algo': ANTIALIAS,
        'content_class': File,

    })

    def index_html(self, instance, REQUEST=None, RESPONSE=None,
                   charset='utf-8', disposition='inline'):
        """Kicks download.
        Writes data including file name and content type to RESPONSE
        """

        if REQUEST is None:
            REQUEST = instance.REQUEST

        if RESPONSE is None:
            RESPONSE = REQUEST.RESPONSE

        RESPONSE.setHeader('Last-Modified', rfc1123_date(instance._p_mtime))
        RESPONSE.setHeader('Content-Type', self.getContentType(instance))
        RESPONSE.setHeader('Accept-Ranges', 'bytes')

        if handleIfModifiedSince(instance, REQUEST, RESPONSE):
            return ''

        scan_redirect = self.scan_on_download(instance, REQUEST, RESPONSE)
        if scan_redirect:
            return scan_redirect

        length = self.get_size(instance)
        RESPONSE.setHeader('Content-Length', length)

        filename = self.getFilename(instance)
        if filename is not None:
            if isinstance(filename, unicode):
                filename = filename.encode(charset, errors="ignore")

            user_agent = REQUEST.get('HTTP_USER_AGENT', '')
            # Microsoft browsers disposition has to be formatted differently
            disposition_default = '{}; filename="{}"; filename={}*=UTF-8'.format(disposition, filename, filename)
            disposition_microsoft = '{}; filename={}; filename*=UTF-8\'\'{}'.format(disposition, filename, quote(filename))
            # use disposition_default by default
            disposition = disposition_default

            if any(key in user_agent for key in ['MSIE', 'WOW64', 'Edge']):
                # Set different dispositon if the user_agent
                # indicates download by a microsoft browser
                disposition = disposition_microsoft

            RESPONSE.setHeader("Content-disposition", disposition)

        request_range = handleRequestRange(instance, length, REQUEST, RESPONSE)

        # Notify file downloads, but do not notify range requests
        if not ('start' in request_range and request_range['start'] > 0):
            portal_state = getMultiAdapter((instance, instance.REQUEST),
                                           name='plone_portal_state')
            if not portal_state.anonymous():
                registry = getUtility(IRegistry)
                user_ids = registry['ftw.file.filesettings.user_ids']
                if portal_state.member().id \
                        and not portal_state.member().id in user_ids:
                    notify(FileDownloadedEvent(instance, filename))

        return self.get(instance).getIterator(**request_range)

    # TODO - do we need e.g. .... security.declareProtected(View, 'download') ?
    def scan_on_download(self, instance, REQUEST, RESPONSE):
        """ For preempting download of the file with a virus scan """
        try:
            from collective.clamav.validator import _scanBuffer
            result = _scanBuffer(instance.data)
            if result:
                msgid = _(
                    u"download_not_possible",
                    default=u"Download not possible because the file contains a virus (${name}).",
                    mapping={u"name": result}
                )

                tx_tool = getToolByName(instance, 'translation_service')
                IStatusMessage(REQUEST).addStatusMessage(tx_tool.translate(msgid), type='error')
                file_view = instance.absolute_url() + "/file_view"
                return RESPONSE.redirect(file_view)
        except ImportError:
            pass

        # Scanning passed - or not available
        return None
