from zope.publisher.browser import BrowserView


class VersionPreview(BrowserView):
    """
    """

    def __call__(self):
        version_id = int(self.request.get('version_id'))
        self.context = self.context.portal_repository.retrieve(
            self.context, version_id).object
        self.context.versioned_context = True
        return super(VersionPreview, self).__call__()
