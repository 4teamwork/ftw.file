from Products.TinyMCE.adapters.JSONDetails import JSONDetails
import json


class FtwJSONDetails(JSONDetails):

    def getDetails(self):
        details_json = super(FtwJSONDetails, self).getDetails()
        details = json.loads(details_json)
        # patch default scale on ftw.file
        for scale in details.get('scales', []):

            if scale['title'] == 'Original':
                scale['value'] = '/@@images/image'
                break

        details_json = json.dumps(details)
        return details_json
