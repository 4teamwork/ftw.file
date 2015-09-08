from Products.Archetypes.utils import shasattr
from ftw.file.interfaces import IFtwFileField
from plone.app.blob.mixins import ImageFieldMixin
from plone.app.imaging.traverse import DefaultImageScaleHandler
from zope.component import adapts
from zope.interface import implementsOnly


class FtwFileImageScaleHandler(DefaultImageScaleHandler):
    adapts(IFtwFileField)

    def getScale(self, instance, scale):
        if self.context.get(instance).content_type.startswith('image/'):
            return super(FtwFileImageScaleHandler, self).getScale(instance,
                                                                  scale)
        else:
            return None


class ImagingMixin(ImageFieldMixin):
    """The goal of this mixin is to get the funtionality and benefits of an
    ImageField while not restricting the current funtionality of the field.
    The problem which surfaced was, that we weren't able to upload files
    anymore that weren't images, because a validator was registered for the
    ImageField to ensure only images are uploaded.
    Therefore we inherit from the ImageFieldMixin and remove its implemented
    interfaces since they are often used to restrict certain behaviours.
    """

    implementsOnly()

    def getScale(self, instance, scale=None, **kwargs):
        """Use Original Archetypes implementation since the one of the mixin
        leads to a loop.
        """

        if scale is None:
            return self.get(instance, **kwargs)
        else:
            id = self.getName() + '_' + scale
            try:
                image = self.getStorage(instance).get(id, instance, **kwargs)
            except AttributeError:
                return ''
            image = self._wrapValue(instance, image, **kwargs)
            if shasattr(image, '__of__', acquire=True) and not kwargs.get(
                    'unwrapped', False):
                return image.__of__(instance)
            else:
                return image
