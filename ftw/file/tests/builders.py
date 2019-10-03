from ftw.builder import builder_registry
from ftw.builder.content import DXFileBuilder
from path import Path
from plone.namedfile.file import NamedBlobImage


class CustomFileBuilder(DXFileBuilder):
    portal_type = 'ftw.file.File'

    def attach_asset(self, filename):
        return self.attach_file_containing(
            self._asset(filename).bytes(), filename)

    def _asset(self, filename):
        path = Path(__file__).dirname().realpath().joinpath('assets', filename)
        return path

    def _attach_dx_file(self, content, name):
        self.attach(NamedBlobImage(data=content, filename=name))
        return self


builder_registry.register('file', CustomFileBuilder, force=True)
