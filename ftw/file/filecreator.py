from ftw.file.interfaces import IFile
from ftw.zipextract.interfaces import IFileCreator
from ftw.zipextract.interfaces import ObjectCreatorBase
from zope.component import adapts
from zope.interface import implements


class FileCreator(ObjectCreatorBase):
    implements(IFileCreator)
    adapts(IFile)
    portal_type = "File"
