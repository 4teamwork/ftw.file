from plone.app.blob import field
from ftw.file import fileMessageFactory as _
from zope.event import notify
from ftw.journal.events.events import JournalEntryEvent
from webdav.common import rfc1123_date


def reencode(filename, charset, charset_fallback, charset_output):
    try:
        filename = unicode(filename, charset).encode(charset_output)
    except (UnicodeDecodeError, UnicodeEncodeError):
        try:
            filename = unicode(filename, charset_fallback).encode(charset_output)
        except (UnicodeDecodeError, UnicodeEncodeError):
            pass # leave unchanged
    return filename


class FileField(field.FileField):
    
    def index_html(self, instance, REQUEST=None, RESPONSE=None, no_output=False, disposition=None):
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
        if filename is not None:
            filename = reencode(filename, 'utf-8', 'ISO-8859-1', 'ISO-8859-1')
            RESPONSE.setHeader("Content-disposition", 'attachment; filename=%s' % filename)

        filename = self.getFilename(instance)

        action = _(u"label_file_downloaded", default=u"File downloaded")
        notify(JournalEntryEvent(instance, filename, action))
        return raw_file
 