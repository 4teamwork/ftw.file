from ZODB.POSException import ConflictError
from logging import exception
from plone.app.imaging.interfaces import IImageScaling, IImageScaleFactory
from plone.app.imaging.scaling import ImageScaling
from zope.component import queryAdapter
from zope.interface import alsoProvides
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse
from zope.traversing.interfaces import ITraversable


class FtwImageScaling(ImageScaling):
    """ view used for generating (and storing) image scales """
    implements(IImageScaling, ITraversable, IPublishTraverse)

    def create(self, fieldname, direction='keep', **parameters):
        """ factory for image scales, see `IImageScaleStorage.scale` """
        field = self.field(fieldname)
        alsoProvides(field, IImageScaleFactory)
        create = queryAdapter(field, IImageScaleFactory).create
        try:
            return create(self.context, direction=direction, **parameters)
        except IOError:
            return None
        except OverflowError:
            # Some PSDs throw an OverflowError, probably because of unsupported
            # file formats.
            # https://github.com/4teamwork/ftw.file/issues/29
            return None
        except (ConflictError, KeyboardInterrupt):
            raise
        except Exception:
            if not getattr(field, 'swallowResizeExceptions', False):
                raise
            else:
                exception('could not scale "%r" of %r',
                          field, self.context.absolute_url())
