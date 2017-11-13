from PIL import Image
from plone import api
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility


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

    registry = getUtility(IRegistry)
    disable_download_redirect = registry.get('ftw.file.disable_download_redirect', False)

    try:
        if disable_download_redirect:
            return False
        plone_view = context.restrictedTraverse('@@plone')
        is_border_visible = plone_view.showEditableBorder()
        return not is_border_visible

    finally:
        if border_was_force_disabled:
            request.other['disable_border'] = border_was_force_disabled
        if border_was_force_enabled:
            request.other['enable_border'] = border_was_force_enabled


def is_image(mimetype):
    Image.init()
    open_handlers = Image.OPEN.keys()
    extensions = []
    for key, value in Image.EXTENSION.items():
        if value in open_handlers:
            extensions.append(key.strip('.'))

    mr = getToolByName(api.portal.get(), 'mimetypes_registry')
    mimetypes = mr.lookup(mimetype)
    if not mimetypes:
        return False  # unknown mimetype

    mime_extensions = mimetypes[0].extensions
    for ext in mime_extensions:
        if ext in extensions:
            return True
    for glob in mr.lookup(mimetype)[0].globs:
        if glob.strip("*.") in extensions:
            return True
    return False


class FileMetadata(object):
    """Handles some metadata of an object.

    The FileMetadata-object provides some properties and functions
    to get different pre-configured metadata of a file-object.
    """
    def __init__(self, context):
        self.context = context

    @property
    def show_author(self):
        """True when the file author should be displayed.

        False: if visitor is anonymous and siteproperty
               'allowAnonymousViewAbout' is False

        True:  if visitor is not anonymous
        True:  if visitor is anonymous and siteproperty
               'allowAnonymousViewAbout' is True
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
        """Returns a dict with id, name and url of the author

        If the author has a fullname it takes it as the name
        If the autor has no fullname or if he have been deleted
        then it takes the userid as the name
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
        """Returns the localized documentDate.
        """
        date = self.context.getDocumentDate()
        return self.context.toLocalizedTime(date)

    @property
    def modified_date(self):
        """Returns the localized modified-date.
        """
        modified = self.context.modified()
        return self.context.toLocalizedTime(modified, long_format=True)

    def get_image_tag(
            self, fieldname, width=None, height=None, direction="down"):
        """Returns the scaled image-tag if an image exists.
        """
        if not self.context.is_image():
            return None
        scale = self.context.restrictedTraverse('@@images')
        img = scale.scale(
            fieldname=fieldname,
            width=width,
            height=height,
            direction=direction)
        if img:
            return img.tag()
        return None

    @property
    def can_edit(self):
        """Returns true if the logged in user has
        modify-permission on the context.
        """
        mtool = getToolByName(self.context, 'portal_membership')
        return mtool.checkPermission('Modify portal content', self.context)
