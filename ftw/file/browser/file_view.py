from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView


class FileView(BrowserView):
    """ View for ftw.file """

    def show_author(self):
        """Checks if the user is anonymous and is not allowAnonymousViewAbout.
        """
        site_props = getToolByName(self.context, 'portal_properties').site_properties
        mt = getToolByName(self.context, 'portal_membership')

        if not site_props.getProperty('allowAnonymousViewAbout', False) \
                and mt.isAnonymousUser():
            return False
        return True

    def get_author(self):
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

    def get_document_date(self):
        """ returns the effectiveDate """
        date = self.context.getDocumentDate()
        try:
            return self.context.toLocalizedTime(date)
        except ValueError:
            return '-'

    def get_modified_date(self):
        """ returns the Modifieddate """
        modified = self.context.modified()
        try:
            return self.context.toLocalizedTime(modified, long_format=True)
        except ValueError:
            return '-'

    def is_image(self):
        allowed_types = [
            'jpeg',
            'jpg',
            'png']

        file_ = self.context.getFile()
        mimetype = file_.getContentType()
        if [allowed for allowed in allowed_types if allowed in mimetype]:
            return True
        return False
