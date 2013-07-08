

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
