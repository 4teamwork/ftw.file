from zope.interface import implements
from ftw.file.interfaces import IFileDownloadedEvent


class FileDownloadedEvent(object):
    """Event to notify when a file is downloaded"""
    implements(IFileDownloadedEvent)

    def __init__(self, obj, filename):
        self.object = obj
        self.filename = filename
