from ftw.file.interfaces import IFile
from plone.app.contenttypes.indexers import SearchableText_file
from plone.indexer.decorator import indexer
from Products.CMFPlone.utils import safe_hasattr
from zope.interface import Interface


@indexer(Interface)
def document_date(obj):
    if safe_hasattr(obj, 'document_date'):
        return obj.document_date


@indexer(IFile)
def SearchableText_ftwfile(obj):
    return SearchableText_file(obj)()
