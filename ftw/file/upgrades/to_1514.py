from ftw.upgrade import UpgradeStep

class ReindexIcons(UpgradeStep):

    def __call__(self):
        cat = self.portal.portal_catalog
        all_values = cat.uniqueValuesFor('getContentType')
        values = []
        for value in all_values:
            if value.startswith('image'):
                values.append(value)
        values.append('application/pdf')
        results = cat({'portal_type':'File', 'getContentType': values})
        for result in results:
            obj = result.getObject()
            cat.reindexObject(obj, idxs=['Title'], update_metadata=True)
