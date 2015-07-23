from Products.CMFCore.utils import getToolByName
from zope.publisher.browser import BrowserView


class VersionPreview(BrowserView):
    """
    """

    def __call__(self):
        version = self.get_version()
        view = version.restrictedTraverse('@@file_preview')
        return view(
            show_history=False,
            actions_list=[
                'open_pdf',
                'download_this_version']
            )

    def get_version(self):
        prtool = getToolByName(self.context, 'portal_repository')
        version_id = int(self.request.get('version_id'))
        return prtool.retrieve(self.context, version_id).object
