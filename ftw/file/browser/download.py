from AccessControl import Unauthorized
from Products.ATContentTypes.browser.download import DownloadArchetypeFile
from zope.publisher.interfaces import NotFound
import urllib


class DownloadFileView(DownloadArchetypeFile):

    def __call__(self):
        if self.fieldname is not None:
            return self.call_download()

        field = self.context.getPrimaryField()
        content = field.get(self.context)
        if not content:
            return self.call_download()

        filename = content.filename
        if isinstance(filename, unicode):
            filename = filename.encode('utf-8')

        # We will use the filename in the url and having a percent sign (even
        # a quoted one) in the url seems to cause problems with apache
        # mod_rewrite and look-ahead variables. Thus remove it.
        filename = filename.replace('%', '')
        filename = urllib.quote(filename)

        download_url = '/'.join((
                self.context.absolute_url(),
                '@@download',
                field.getName(),
                filename))

        return self.request.RESPONSE.redirect(download_url)

    def call_download(self):
        context = getattr(self.context, 'aq_explicit', self.context)
        field = context.getField(self.fieldname)
        if field is None:
            raise NotFound(self, self.fieldname, self.request)
        if not field.checkPermission('r', context):
            raise Unauthorized()

        return field.index_html(context, disposition='attachment')
