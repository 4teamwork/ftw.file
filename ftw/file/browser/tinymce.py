from plone.app.uuid.utils import uuidToObject
from Products.TinyMCE.adapters.JSONFolderListing import JSONFolderListing
import json


class FtwJSONFolderListing(JSONFolderListing):

    def getListing(self, filter_portal_types, rooted, document_base_url,
                   upload_type=None, image_types=None):
        listing = super(FtwJSONFolderListing, self).getListing(
            filter_portal_types, rooted, document_base_url,
            upload_type=upload_type, image_types=image_types)
        if upload_type == 'Image':
            listing = self.remove_files_which_are_not_images(listing)
        return listing

    def remove_files_which_are_not_images(self, json_encoded_listing):
        """The super getListing call returns all ftw.file files, no matter
        if they are images or not.
        When we require images, we therefore need to filter the files so
        that we only return images.
        """

        listing_obj = json.loads(json_encoded_listing)

        filtered_items = []
        for item in listing_obj['items']:
            obj = uuidToObject(item['uid'])
            if hasattr(obj, 'is_image') and not obj.is_image():
                continue
            filtered_items.append(item)
        listing_obj['items'] = filtered_items

        return json.dumps(listing_obj)
