from Products.ATContentTypes.interfaces import IFileContent
from zope.interface import Attribute
from zope.component.interfaces import IObjectEvent


class IFile(IFileContent):
    """File marker interface.
    """


class IFileDownloadedEvent(IObjectEvent):
    """An event fired when a file is downloaded"""

    context = Attribute("The file object that was downloaded")

