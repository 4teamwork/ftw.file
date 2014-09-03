from ftw.activity.browser.representations import DefaultRepresentation
from ftw.file.interfaces import IFile
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import adapts
from zope.interface import Interface


class FileRepresentation(DefaultRepresentation):
    adapts(IFile, Interface)
    index = ViewPageTemplateFile('activity.pt')

    def get_image_tag(self):
        if not self.context.is_image():
            return None
        scale = self.context.restrictedTraverse('@@images')
        img = scale.scale('file', height=100, direction='down')
        if img:
            return img.tag()
        return None
