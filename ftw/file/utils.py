from Products.CMFCore.utils import getToolByName


def redirect_to_download_by_default(context):
    """Returns True if the default view of the file (context) should
    redirect to the download view.
    """

    request = context.REQUEST

    border_was_force_disabled = request.get('disable_border')
    if border_was_force_disabled:
        del request.other['disable_border']

    border_was_force_enabled = request.get('enable_border')
    if border_was_force_enabled:
        del request.other['enable_border']

    try:
        plone_view = context.restrictedTraverse('@@plone')
        is_border_visible = plone_view.showEditableBorder()
        return not is_border_visible

    finally:
        if border_was_force_disabled:
            request.other['disable_border'] = border_was_force_disabled
        if border_was_force_enabled:
            request.other['enable_border'] = border_was_force_enabled


def format_filesize(num):
    for unit in ('B', 'KB', 'MB'):
        if abs(num) < 1024.0:
            return "%3.1f %s" % (num, unit)
        num /= 1024.0
    return "%.1f %s" % (num, 'GB')


class FileMetadata(object):
    """Handles some metadata of an object
    """
    def __init__(self, context):
        self.context = context

    @property
    def show_author(self):
        """Checks if the user is anonymous and is not allowAnonymousViewAbout.
        """
        site_props = getToolByName(
            self.context, 'portal_properties').site_properties
        mt = getToolByName(self.context, 'portal_membership')

        if not site_props.getProperty('allowAnonymousViewAbout', False) \
                and mt.isAnonymousUser():
            return False
        return True

    @property
    def author(self):
        """ returns the fullname from creator or the id if there isn't a
            fullname.
        """
        pm = getToolByName(self.context, 'portal_membership')
        userid = self.context.Creator()
        member = pm.getMemberById(userid)
        if member:
            return dict(id=userid,
                        name=member.getProperty('fullname') or userid,
                        url=self.context.portal_url() + '/author/' + userid)
        return dict(id=userid,
                    name=userid,
                    url='')

    @property
    def document_date(self):
        """ returns the effectiveDate """
        date = self.context.getDocumentDate()
        try:
            return self.context.toLocalizedTime(date)
        except ValueError:
            return '-'

    @property
    def modified_date(self):
        """ returns the Modifieddate """
        modified = self.context.modified()
        try:
            return self.context.toLocalizedTime(modified, long_format=True)
        except ValueError:
            return '-'

    def get_image_tag(self, scale, width, direction):
        if not self.context.is_image():
            return None
        scale = self.context.restrictedTraverse('@@images')
        img = scale.scale(scale, width=width, direction=direction)
        if img:
            return img.tag()
        return None

    @property
    def can_edit(self):
        mtool = getToolByName(self.context, 'portal_membership')
        return mtool.checkPermission('Modify portal content', self.context)
