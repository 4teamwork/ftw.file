from Products.ATContentTypes.interfaces import IFileContent
from zope.component.interfaces import IObjectEvent
from zope.interface import Attribute
from plone.app.blob.interfaces import IBlobField


class IFile(IFileContent):
    """File marker interface.
    """


class IFileDownloadedEvent(IObjectEvent):
    """An event fired when a file is downloaded"""

    context = Attribute("The file object that was downloaded")


class IFtwFileField(IBlobField):
    """FileField marker"""
