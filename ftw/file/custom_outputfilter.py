from plone.outputfilters.filters import resolveuid_and_caption
from plone.app.imaging.interfaces import IImageScale


class FtwFileFilter(resolveuid_and_caption.ResolveUIDAndCaptionFilter):

    def resolve_image(self, src):
        (image, fullimage, source, description) = resolveuid_and_caption.\
            ResolveUIDAndCaptionFilter.resolve_image(self, src)
        if not IImageScale.providedBy(image):
            url = ''
            obj, subpath, appendix = self.resolve_link(src)
            if image:
                url = image.absolute_url()
            if isinstance(url, unicode):
                url = url.encode('utf8')
            src = '/'.join([url, subpath, appendix])
        else:
            src = image.absolute_url()
        return image, fullimage, src, description
