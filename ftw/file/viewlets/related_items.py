from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.content import ContentRelatedItems
from Products.CMFCore.utils import getToolByName


class FileRelatedItems(ContentRelatedItems):

    index = ViewPageTemplateFile("related_items.pt")

    def referenced_by(self):
        mem_tool = getToolByName(self.context, 'portal_membership')
        backrefs = self.context.getBackReferences()
        related_items = self.context.getRawRelatedItems()
        backref_list = []
        for item in backrefs:
            if not item.UID() in related_items and mem_tool.checkPermission(
                'View', item):
                backref_list.append(item)
        return backref_list
