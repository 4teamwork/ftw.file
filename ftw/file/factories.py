# -*- coding: utf-8 -*-
from zope.interface import implementer
from plone.namedfile.storages import MAXCHUNKSIZE
from plone.namedfile.interfaces import IStorage

# Copied from plone.app.z3form 3.1.0
@implementer(IStorage)
class Zope2FileUploadStorable(object):

    def store(self, data, blob):
        data.seek(0)
        with blob.open('w') as fp:
            block = data.read(MAXCHUNKSIZE)
            while block:
                fp.write(block)
                block = data.read(MAXCHUNKSIZE)