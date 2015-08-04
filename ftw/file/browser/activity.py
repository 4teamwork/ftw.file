from ftw.activity.browser.representations import DefaultRepresentation
from ftw.file.interfaces import IFile
from ftw.file.utils import FileMetadata
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import adapts
from zope.interface import Interface


class FileRepresentation(DefaultRepresentation):
    adapts(IFile, Interface)
    index = ViewPageTemplateFile('activity.pt')

    def get_image_tag(self):
        return FileMetadata(self.context).get_image_tag(
            fieldname='file', height=100)
