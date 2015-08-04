from ftw.file import fileMessageFactory as _
from Products.CMFCore.utils import getToolByName
from zope.i18n import translate
from zope.publisher.browser import BrowserView


class VersionPreview(BrowserView):
    """
    """

    def __call__(self):
        version = self.get_version()
        view = version.restrictedTraverse('@@file_preview')

        return view(
            documentTitle=translate(_(
                u'file_version_title',
                default=u'${title} - Version ${version} of ${version_num}',
                mapping={
                    u'title': version.Title().decode('utf-8'),
                    u'version': version.version_id + 1,
                    u'version_num': self.context.version_id + 1}),
                context=self.context.REQUEST),
            show_history=False,
            actions_list=[
                'goto_original_file',
                'open_pdf',
                'download_this_version']
            )

    def get_version(self):
        prtool = getToolByName(self.context, 'portal_repository')
        version_id = int(self.request.get('version_id'))
        return prtool.retrieve(self.context, version_id).object
