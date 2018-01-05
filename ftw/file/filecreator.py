from ftw.file.content.file import File
from ftw.zipextract.interfaces import IFileCreator
from ftw.zipextract.interfaces import _ObjectCreator
from zope.component import adapts
from zope.interface import implements


class FileCreator(_ObjectCreator):
    implements(IFileCreator)
    adapts(File)
    portal_type = "File"
