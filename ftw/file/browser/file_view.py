from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ftw.file.utils import FileMetadata
from Products.Five import BrowserView


class FileView(BrowserView):
    """ View for ftw.file """

    template = ViewPageTemplateFile('file_view.pt')

    def __call__(self):
        return self.template()

    def get_image_tag(self):
        return self.metadata.get_image_tag(
            fieldname='file', width=200)

    @property
    def metadata(self):
        if not hasattr(self, '_metadata'):
            self._metadata = FileMetadata(self.context)
        return self._metadata
