from ftw.upgrade import UpgradeStep
from Products.CMFPlone.utils import getToolByName


class UpdateContenttype(UpgradeStep):

    def __call__(self):
        mtr = getToolByName(self.portal, 'mimetypes_registry')
        cat = getToolByName(self.portal, 'portal_catalog')
        contenttypes = ['application/msword', 'application/octet-stream']
        query = {'portal_type': 'File', 'getContentType': contenttypes}
        for obj in self.objects(query, 'update Contenttype'):
            file_ = obj.getField('file').get(obj)
            mimetype = mtr.classify(file_.data, filename=file_.getFilename())
            if str(mimetype) != file_.getContentType():
                file_.setContentType(str(mimetype))
                cat.reindexObject(obj,
                                  idxs=['getContentType'],
                                  update_metadata=True
                                  )
