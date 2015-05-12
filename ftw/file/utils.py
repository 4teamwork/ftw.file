from PIL import Image
from plone import api
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


def is_image(file_):
    mimetype = file_.getContentType()
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
