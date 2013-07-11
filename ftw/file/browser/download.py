from Products.ATContentTypes.browser.download import DownloadArchetypeFile


class DownloadFileView(DownloadArchetypeFile):

    def __call__(self):
        if self.fieldname is not None:
            return super(DownloadFileView, self).__call__()

        field = self.context.getPrimaryField()
        content = field.get(self.context)
        if not content:
            return super(DownloadFileView, self).__call__()

        filename = content.filename
        download_url = '/'.join((
                self.context.absolute_url(),
                '@@download',
                field.getName(),
                filename))

        return self.request.RESPONSE.redirect(download_url)
