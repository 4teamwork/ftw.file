from collective.prettydate.interfaces import IPrettyDate
from ftw.bumblebee.mimetypes import get_mimetype_image_url
from ftw.bumblebee.mimetypes import get_mimetype_title
from ftw.bumblebee.mimetypes import is_mimetype_supported
from ftw.bumblebee.utils import get_representation_url
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.viewlet.interfaces import IViewlet
from zope.viewlet.interfaces import IViewletManager


def format_filesize(num):
    for unit in ('B', 'KB', 'MB'):
        if abs(num) < 1024.0:
            return "%3.1f %s" % (num, unit)
        num /= 1024.0
    return "%.1f %s" % (num, 'GB')


class FilePreview(BrowserView):
    """ View for ftw.file with document preview functionality"""

    def thumbnail_url(self):
        portal_url = getToolByName(self.context, 'portal_url')()
        fallback_url = "{0}/spinner.gif".format(portal_url)
        return get_representation_url('thumbnail', obj=self.context, fallback_url=fallback_url)

    def preview_url(self):
        portal_url = getToolByName(self.context, 'portal_url')()
        fallback_url = "{0}/spinner.gif".format(portal_url)
        return get_representation_url('preview', obj=self.context, fallback_url=fallback_url)

    def get_file_info(self):
        mimetype = self.context.getContentType()
        filename = self.context.getPrimaryField().getFilename(self.context)
        filesize = self.context.getPrimaryField().get_size(self.context)

        return {'mimetype_icon_url': get_mimetype_image_url(mimetype),
                'mimetype_title': get_mimetype_title(mimetype),
                'file_url': self.context.absolute_url() + '/download',
                'filename': filename,
                'filesize': format_filesize(filesize)}

    def get_preview_pdf_url(self):
        portal_url = getToolByName(self.context, 'portal_url')()
        preview_fallback = portal_url + '/iframe_preview_not_available'
        return get_representation_url('preview',
                                      obj=self.context,
                                      fallback_url=preview_fallback)

    def get_pdf_info(self):
        mimetype = self.context.getContentType()
        if mimetype == 'application/pdf':
            return False

        if not is_mimetype_supported(mimetype):
            return False

        portal_url = getToolByName(self.context, 'portal_url')()
        fallback_url = portal_url + '/preview_not_available'
        pdf_url = get_representation_url('pdf', obj=self.context,
                                         fallback_url=fallback_url)

        return {'mimetype_icon_url': get_mimetype_image_url('application/pdf'),
                'mimetype_title': get_mimetype_title('application/pdf'),
                'pdf_url': pdf_url}

    def get_journal(self):
        viewlet = self.get_content_history_viewlet()
        date_utility = getUtility(IPrettyDate)

        for item in viewlet.fullHistory() or ():
            comment = item['comments']
            if comment.strip() == '-':
                comment = ''

            yield {'time': item['time'],
                   'relative_time': date_utility.date(item['time']),
                   'action': item['transition_title'],
                   'actor': self.get_user_info(item['actorid']),
                   'actor_name': item['actorid'],
                   'comment': comment,
                   'downloadable_version': item['type'] == 'versioning',
                   'version_id': item.get('version_id')}

    def get_content_history_viewlet(self):
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

    def get_user_info(self, userid):
        if not userid:
            return None

        membership_tool = getToolByName(self.context, 'portal_membership')
        member = membership_tool.getMemberById(userid)
        return {'userid': userid,
                'fullname': member.getProperty('fullname') or userid,
                'portrait_url': membership_tool.getPersonalPortrait(userid).absolute_url()}
