from plone.outputfilters.filters.resolveuid_and_caption import ResolveUIDAndCaptionFilter

class FtwFileFilter(ResolveUIDAndCaptionFilter):

    def resolve_image(self, src):
        (image, fullimage, source, description) = ResolveUIDAndCaptionFilter.resolve_image(self, src)

        url = ''
        obj, subpath, appendix = self.resolve_link(src)
        if image:
            url = image.absolute_url()
        if isinstance(url, unicode):
            url = url.encode('utf8')
        src = '/'.join([url, subpath, appendix])

        return image, fullimage, src, description
