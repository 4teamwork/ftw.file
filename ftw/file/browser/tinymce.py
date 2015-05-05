from plone.app.uuid.utils import uuidToObject
from Products.TinyMCE.adapters.JSONFolderListing import JSONFolderListing
import json


class FtwJSONFolderListing(JSONFolderListing):

    def getListing(self, *args, **kwargs):
        listing = super(FtwJSONFolderListing, self).getListing(*args, **kwargs)
        listing_obj = json.loads(listing)

        filtered_items = []
        for item in listing_obj['items']:
            obj = uuidToObject(item['uid'])
            if hasattr(obj, 'is_image') and not obj.is_image():
                continue
            filtered_items.append(item)
        listing_obj['items'] = filtered_items

        return json.dumps(listing_obj)
