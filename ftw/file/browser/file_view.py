from ftw.file.utils import FileMetadata
from Products.Five import BrowserView


class FileView(BrowserView):
    """ View for ftw.file """

    def __call__(self):
        self.metadata = FileMetadata(self.context)
        return super(FileView, self).__call__()

    def get_image_tag(self):
        return self.metadata.get_image_tag(
            fieldname='file', width=200)
