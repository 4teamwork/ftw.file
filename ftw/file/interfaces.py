from plone.app.blob.interfaces import IBlobField
from zope.component.interfaces import IObjectEvent
from zope.interface import Attribute
from zope.interface import Interface


class IFile(Interface):
    """File marker interface.
    """


class IFileDownloadedEvent(IObjectEvent):
    """An event fired when a file is downloaded"""

    context = Attribute("The file object that was downloaded")


class IFtwFileField(IBlobField):
    """FileField marker"""
