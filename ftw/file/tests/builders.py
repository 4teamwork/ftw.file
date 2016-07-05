from ftw.builder import builder_registry
from ftw.builder.content import ATFileBuilder
from path import Path


class CustomFileBuilder(ATFileBuilder):

    def attach_asset(self, filename):
        return self.attach_file_containing(
            self._asset(filename).bytes(), filename)

    def _asset(self, filename):
        path = Path(__file__).dirname().realpath().joinpath('assets', filename)
        return path


builder_registry.register('file', CustomFileBuilder, force=True)
