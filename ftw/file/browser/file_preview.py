from collective.prettydate.interfaces import IPrettyDate
from ftw.bumblebee.mimetypes import get_mimetype_image_url
from ftw.bumblebee.mimetypes import get_mimetype_title
from ftw.bumblebee.mimetypes import is_mimetype_supported
from ftw.bumblebee.utils import get_representation_url
from ftw.file import fileMessageFactory as _
from ftw.file.browser.file_view import FileView
from ftw.file.interfaces import IFilePreviewActions
from ftw.file.interfaces import IFilePreviewJournal
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.i18n import translate
from zope.viewlet.interfaces import IViewlet
from zope.viewlet.interfaces import IViewletManager


def format_filesize(num):
    for unit in ('B', 'KB', 'MB'):
        if abs(num) < 1024.0:
            return "%3.1f %s" % (num, unit)
        num /= 1024.0
    return "%.1f %s" % (num, 'GB')


class FilePreviewJournal(object):
    """
    """
    def __init__(self, context):
        self.context = context
        self.request = context.REQUEST

    def __call__(self):
        return self.get_journal()

    def get_journal(self):
        viewlet = self._get_content_history_viewlet()
        date_utility = getUtility(IPrettyDate)
        journal_items = []
        for item in viewlet.fullHistory() or ():
            journal_items.append({
                'time': item['time'],
                'relative_time': date_utility.date(item['time']),
                'action': item['transition_title'],
                'actor': self._get_user_info(item['actorid']),
                'comment': item['comments'],
                'downloadable_version': item['type'] == 'versioning',
                'version_id': item.get('version_id')})
        return journal_items

    def _get_content_history_viewlet(self):
        view = getMultiAdapter((self.context, self.request),
                               name='file_view')
        manager = getMultiAdapter((self.context, self.request, view),
                                  IViewletManager,
                                  name='plone.belowcontentbody')
        viewlet = getMultiAdapter((self.context, self.request, view, manager),
                                  IViewlet,
                                  name='plone.belowcontentbody.inlinecontenthistory')
        viewlet.update()
        return viewlet

    def _get_user_info(self, userid):
        if not userid:
            return None

        membership_tool = getToolByName(self.context, 'portal_membership')
        member = membership_tool.getMemberById(userid)
        if not member:
            return userid
        return member.getProperty('fullname') or userid


class FilePreviewActions(object):
    """
    """
    def __init__(self, context):
        self.context = context
        self.request = context.REQUEST

    def __call__(self, actions_to_list=[]):
        return self.get_actions(actions_to_list)

    def get_actions(self, actions_to_list=[]):
        actions_list = []
        for action in actions_to_list:
            action_function = getattr(self, "_action_{0}".format(action), None)
            if not action_function:
                continue

            action_value = action_function()
            if not action_value:
                continue

            actions_list.append(action_value)
        return actions_list

    def _action_download_original(self):
        mimetype = self.context.getContentType()
        return {
            'url': self.context.absolute_url() + '/download',
            'target': '_top',
            'cssclass': 'original-file-link',
            'image': {'src': get_mimetype_image_url(mimetype),
                      'title': get_mimetype_title(mimetype),
                      'alt': get_mimetype_title(mimetype),
                      'cssclass': 'mimetype_icon'},
            'text': translate(_(
                u'file_metadata_download_original',
                default=u'Download Original'),
                context=self.context.REQUEST)
        }

    def _action_open_pdf(self):
        mimetype = self.context.getContentType()
        if mimetype == 'application/pdf':
            return {}

        if not is_mimetype_supported(mimetype):
            return {}

        portal_url = getToolByName(self.context, 'portal_url')()
        fallback_url = portal_url + '/preview_not_available'
        return {
            'url': get_representation_url(
                'pdf', obj=self.context, fallback_url=fallback_url),
            'target': '_top',
            'cssclass': 'pdf-file-link',
            'image': {'src': get_mimetype_image_url('application/pdf'),
                      'title': get_mimetype_title('application/pdf'),
                      'alt': get_mimetype_title('application/pdf'),
                      'cssclass': 'mimetype_icon'},
            'text': translate(
                _(u'file_metadata_open_pdf', default=u'Open PDF'),
                context=self.context.REQUEST)
        }

    def _action_delete(self):
        if not _checkPermission("Delete objects", self.context):
            return {}
        return {
            'url': "{0}/delete_confirmation".format(
                self.context.absolute_url()),
            'target': '_top',
            'cssclass': 'delete-object-link',
            'image': None,
            'text': translate(
                _(u'file_metadata_delete_file', default=u'Delete File'),
                context=self.context.REQUEST)
        }

    def _action_edit(self):
        if not _checkPermission("Modify portal content", self.context):
            return {}

        return {
            'url': "{0}/edit".format(
                self.context.absolute_url()),
            'target': '_top',
            'cssclass': 'edit-object-link',
            'image': None,
            'text': translate(
                _(u'file_metadata_edit_file', default=u'Edit File'),
                context=self.context.REQUEST)
        }

    def _action_download_this_version(self):
        mimetype = self.context.getContentType()
        return {
            'url': "{0}/file_download_version?version_id={1}".format(
                self.context.absolute_url(), self.context.version_id),
            'target': '_top',
            'cssclass': 'download-version-link',
            'image': {'src': get_mimetype_image_url(mimetype),
                      'title': get_mimetype_title(mimetype),
                      'alt': get_mimetype_title(mimetype),
                      'cssclass': 'mimetype_icon'},
            'text': translate(
                _(u'file_metadata_download_this_version',
                  default=u'Download this version'),
                context=self.context.REQUEST)
        }


class FilePreview(FileView):
    """ View for ftw.file with document preview functionality
    """

    default_actions_list = [
        'open_pdf',
        'download_original',
        'edit',
        'delete']

    def __call__(self, show_history=True, actions_list=default_actions_list):
        self.show_history = show_history
        self.actions_list = actions_list
        return super(FilePreview, self).__call__()

    def actions(self):
        return IFilePreviewActions(self.context)(self.actions_list)

    def journal(self):
        if not self.show_history:
            return []
        return IFilePreviewJournal(self.context)()

    def get_fallback_url(self):
        portal_url = getToolByName(self.context, 'portal_url')()
        return "{0}/++resource++ftw.file.resources/image_not_found.png".format(
            portal_url)

    def get_preview_pdf_url(self):
        return get_representation_url('preview',
                                      obj=self.context,
                                      fallback_url=self.get_fallback_url())

    def get_file_info(self):
        mimetype = self.context.getContentType()
        filename = self.context.getPrimaryField().getFilename(self.context)
        filesize = self.context.getPrimaryField().get_size(self.context)

        return {'mimetype_icon_url': get_mimetype_image_url(mimetype),
                'mimetype_title': get_mimetype_title(mimetype),
                'file_url': self.context.absolute_url() + '/download',
                'filename': filename,
                'filesize': format_filesize(filesize),
                'modified': self.get_modified_date(),
                'created': self.get_document_date(),
                'author': self.get_author()}

    def get_version_preview_image_url(self, version_id):
        prtool = getToolByName(self.context, 'portal_repository')
        version_context = prtool.retrieve(self.context, version_id).object
        representation_url = get_representation_url(
            'thumbnail',
            obj=version_context,
            fallback_url=self.get_fallback_url())

        return representation_url
