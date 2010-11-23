from plone.app.layout.viewlets import content
from Products.CMFCore.utils import _checkPermission


class ContentHistoryViewlet(content.ContentHistoryViewlet):
    """ History viewlet for ftw.file """
    def show_viewlet(self):
        """ Permission Access previous versions is required"""
        if _checkPermission('CMFEditions: Access previous versions',
                             self.context):
            return True
        return False
