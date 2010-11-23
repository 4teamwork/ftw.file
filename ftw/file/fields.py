from plone.app.blob import field
from ftw.file import fileMessageFactory as _
from zope.event import notify
from ftw.journal.events.events import JournalEntryEvent
from Products.Archetypes.utils import contentDispositionHeader


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
        filename = self.getFilename(instance)
        if filename is not None:
            # IE, Safari fix: they can not handle utf8 encoded filenames in content disposition headers 
            user_agent = REQUEST.get('HTTP_USER_AGENT', '')
            if 'MSIE' in user_agent or 'Safari' in user_agent:
                filename = reencode(filename, 'utf-8', 'ISO-8859-1', 'ISO-8859-1')
                RESPONSE.setHeader("Content-disposition", 'attachment; filename=%s' % filename)
            else:
                filename = reencode(filename, 'utf-8', 'ISO-8859-1', 'utf-8')
                header_value = contentDispositionHeader('attachment', instance.getCharset(), filename=filename)
                RESPONSE.setHeader("Content-disposition", header_value)

        action = _(u"label_file_downloaded", default=u"File downloaded")
        notify(JournalEntryEvent(instance, filename, action))
        return raw_file
