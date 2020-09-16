from plone.indexer.decorator import indexer
from Products.CMFPlone.utils import safe_hasattr
from zope.interface import Interface


@indexer(Interface)
def document_date(obj):
    if safe_hasattr(obj, 'document_date'):
        return obj.document_date
