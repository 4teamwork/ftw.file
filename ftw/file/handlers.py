from ftw.file import fileMessageFactory as _
from plone import api
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Products.CMFPlone.utils import safe_unicode
from zope.i18n import translate


def handle_protected_file(obj, event):
    if IPloneSiteRoot.providedBy(event.object):
        # The Plone site is being deleted.
        return

    if obj.is_protected:
        api.portal.show_message(
            message=translate(
                _(
                    u'message_protected_file',
                    default=u'You are not allowed to delete the file "${file_title}".',
                    mapping={
                        'file_title': safe_unicode(obj.Title()),
                    },
                ),
                context=obj.REQUEST,
            ),
            request=obj.REQUEST,
            type='error'
        )
        raise ValueError('Unable to delete a protected file.')
