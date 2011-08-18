from logging import exception
from Acquisition import aq_base
from ZODB.POSException import ConflictError
from OFS.Image import Pdata
from zope.interface import implements
from zope.traversing.interfaces import ITraversable, TraversalError
from zope.publisher.interfaces import IPublishTraverse, NotFound
from plone.app.imaging.interfaces import IImageScaling, IImageScaleFactory
from plone.app.imaging.scale import ImageScale
from plone.scale.storage import AnnotationStorage
from plone.scale.scale import scaleImage
from Products.Five import BrowserView
from zope.component import queryAdapter
from zope.interface import alsoProvides
from plone.app.imaging.scaling import ImageScaling


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
        except (ConflictError, KeyboardInterrupt):
            raise
        except Exception:
            if not field.swallowResizeExceptions:
                raise
            else:
                exception('could not scale "%r" of %r',
                    field, self.context.absolute_url())

