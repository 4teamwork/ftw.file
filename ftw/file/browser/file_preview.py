from collective.prettydate.interfaces import IPrettyDate
from ftw.bumblebee.mimetypes import get_mimetype_image_url
from ftw.bumblebee.mimetypes import get_mimetype_title
from ftw.bumblebee.mimetypes import is_mimetype_supported
from ftw.bumblebee.utils import get_representation_url
from ftw.file import fileMessageFactory as _
from ftw.file.browser.file_view import FileView
from ftw.file.interfaces import IFilePreviewActionsCollector
from ftw.file.interfaces import IFilePreviewFileInfoCollector
from ftw.file.interfaces import IFilePreviewJournal
from ftw.file.interfaces import IFilePreviewCollectorDefaultLists
from ftw.file.utils import format_filesize
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.i18n import translate
from zope.viewlet.interfaces import IViewlet
from zope.viewlet.interfaces import IViewletManager


class FilePreviewJournal(object):
    """
    """
    def __init__(self, context):
        self.context = context
        self.request = context.REQUEST

    def __call__(self, preview_fallback_url=""):
        self.preview_fallback_url = preview_fallback_url
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
                'version_id': item.get('version_id'),
                'version_preview_image_url':
                    self._get_version_preview_image_url(
                        item.get('version_id'))})
        return journal_items

    def _get_content_history_viewlet(self):
        view = getMultiAdapter(
            (self.context, self.request), name='file_view')
        manager = getMultiAdapter(
            (self.context, self.request, view),
            IViewletManager, name='plone.belowcontentbody')
        viewlet = getMultiAdapter(
            (self.context, self.request, view, manager),
            IViewlet, name='plone.belowcontentbody.inlinecontenthistory')
        viewlet.update()
        return viewlet

    def _get_user_info(self, userid):
        membership_tool = getToolByName(self.context, 'portal_membership')
        member = membership_tool.getMemberById(userid)

        if not member:
            return userid
        return member.getProperty('fullname') or userid

    def _get_version_preview_image_url(self, version_id):
        if version_id is None:
            return ""
        prtool = getToolByName(self.context, 'portal_repository')
        version_context = prtool.retrieve(self.context, version_id).object
        representation_url = get_representation_url(
            'thumbnail',
            obj=version_context,
            fallback_url=self.preview_fallback_url)

        return representation_url


class FilePreviewCollector(object):
    """Returns a list with collected data.

    Calls each function defined in collector_list
    and adds appends the returned value to the list.
    The prefix _data_ will be prepended to the function-names.
    """
    def __init__(self, context, browserview):
        self.context = context
        self.view = browserview
        self.function_prefix = '_data_'

    def __call__(self, collector_list=[]):
        return self.collect(collector_list)

    def collect(self, collector_list=[]):
        collected = []
        for function_name in collector_list:
            function_ = getattr(self, "{0}{1}".format(
                self.function_prefix, function_name), None)

            if not function_:
                continue

            info_value = function_()
            if not info_value:
                continue

            collected.append(info_value)
        return collected


class FilePreviewFileInfoCollector(FilePreviewCollector):
    """
    """
    def _data_mimetype_and_filesize(self):
        mimetype = self.context.getContentType()
        filesize = self.context.getPrimaryField().get_size(self.context)
        return {
            'leftcolumn': get_mimetype_title(mimetype),
            'rightcolumn': format_filesize(filesize),
        }

    def _data_filename(self):
        return {
            'leftcolumn': translate(_(
                u'file_metadata_filenname_info',
                default=u'Filename:'),
                context=self.context.REQUEST),
            'rightcolumn': self.context.getPrimaryField().getFilename(
                self.context),
        }

    def _data_modified_date(self):
        return {
            'leftcolumn': translate(_(
                u'file_metadata_dates',
                default=u'Modified:'),
                context=self.context.REQUEST),
            'rightcolumn': self.view.get_modified_date(),
        }

    def _data_document_date(self):
        return {
            'leftcolumn': translate(_(
                u'file_metadata_documentdate',
                default=u'Documentdate:'),
                context=self.context.REQUEST),
            'rightcolumn': self.view.get_document_date(),
        }

    def _data_author(self):
        if not self.view.show_author():
            return {}
        author = self.view.get_author()
        authorname = author.get('name')
        if author.get('url', None):
            authorname = "<a href='{0}'>{1}</a>".format(
                author.get('url'), authorname)

        return {
            'leftcolumn': translate(_(
                u'file_metadata_author',
                default=u'Author:'),
                context=self.context.REQUEST),
            'rightcolumn': authorname,
        }

    def _data_description(self):
        description = self.context.Description()
        if not description:
            return {}
        return {
            'leftcolumn': translate(_(
                u'file_metadata_description',
                default=u'Description:'),
                context=self.context.REQUEST),
            'rightcolumn': description,
        }


class FilePreviewActionsCollector(FilePreviewCollector):
    """
    """
    def _data_download_original(self):
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

    def _data_open_pdf(self):
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

    def _data_delete(self):
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

    def _data_edit(self):
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

    def _data_download_this_version(self):
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

    def _data_goto_original_file(self):
        if not _checkPermission("Modify portal content", self.context):
            return {}

        return {
            'url': self.context.absolute_url(),
            'target': '_top',
            'cssclass': 'goto-original-version-link',
            'image': None,
            'text': translate(
                _(u'file_metadata_goto_original',
                  default=u'Open original document'),
                context=self.context.REQUEST)
        }

    def _data_external_edit(self):
        actions_tool = getToolByName(self.context, 'portal_actions')

        # Do not check condition because its a bad condition
        action = actions_tool.listActionInfos(
            'document_actions/extedit',
            object=self.context,
            check_visibility=1,
            check_permissions=1,
            check_condition=0)

        if not action:
            return {}

        return {
            'url': "{0}/external_edit".format(self.context.absolute_url()),
            'target': '_top',
            'cssclass': 'external-edit-link',
            'image': None,
            'text': translate(
                _(u'file_metadata_external_edit',
                  default=u'Open in external editor'),
                context=self.context.REQUEST)
        }


class FilePreviewCollectorDefaultLists(object):
    """Returns the default list
    """
    _list_actions_list = [
        'open_pdf',
        'download_original',
        'edit',
        'external_edit'
        'delete']

    _list_file_infos_list = [
        'mimetype_and_filesize',
        'filename',
        'modified_date',
        'document_date',
        'author',
        'description']

    def __init__(self, context, browserview):
        self.context = context
        self.view = browserview
        self.list_prefix = "_list_"

    def __call__(self, listname):
        collectorlist = getattr(self, "{0}{1}".format(
            self.list_prefix, listname), None)

        return collectorlist and collectorlist or []


class FilePreview(FileView):
    """ View for ftw.file with document preview functionality
    """
    def __call__(
            self,
            documentTitle=None,
            show_history=True,
            actions_list=[],
            file_infos_list=[],
            preview_fallback_url="",
            ):
        self.documentTitle = documentTitle
        self.show_history = show_history
        self.actions_list = actions_list and actions_list or \
            self._get_collector_list('actions_list')
        self.file_infos_list = file_infos_list and file_infos_list or \
            self._get_collector_list('file_infos_list')
        self.preview_fallback_url = \
            preview_fallback_url or self._get_preview_fallback_url()
        return super(FilePreview, self).__call__()

    def actions(self):
        return getMultiAdapter(
            (self.context, self),
            IFilePreviewActionsCollector)(self.actions_list)

    def fileinfos(self):
        return getMultiAdapter(
            (self.context, self),
            IFilePreviewFileInfoCollector)(self.file_infos_list)

    def journal(self):
        if not self.show_history:
            return []
        return IFilePreviewJournal(self.context)(
            preview_fallback_url=self.preview_fallback_url)

    def title(self):
        if self.documentTitle:
            return self.documentTitle
        return self.context.Title()

    def get_preview_pdf_url(self):
        return get_representation_url('preview',
                                      obj=self.context,
                                      fallback_url=self.preview_fallback_url)

    def _get_preview_fallback_url(self):
        portal_url = getToolByName(self.context, 'portal_url')()
        return "{0}/++resource++ftw.file.resources/image_not_found.png".format(
            portal_url)

    def _get_collector_list(self, listname):
        adapter = getMultiAdapter(
            (self.context, self), IFilePreviewCollectorDefaultLists)
        return adapter(listname)
