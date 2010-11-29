from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView


class FileView(BrowserView):
    """ View for ftw.file """

    def get_author(self):
        """ returns the fullname from creator or the id if there isn't a
            fullname.
        """
        pm = getToolByName(self.context, 'portal_membership')
        userid = self.context.Creator()
        member = pm.getMemberById(userid)
        if member:
            return dict(id = userid,
                        name = member.getProperty('fullname') or userid,
                        url = member.absolute_url())
        return dict(id = userid,
                    name = userid,
                    url = '')

    def get_effective_date(self):
        """ returns the effectiveDate """
        effective = self.context.effective()
        try:
            return self.context.toLocalizedTime(effective)
        except ValueError:
            return '-'