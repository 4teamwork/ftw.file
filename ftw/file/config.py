from Products.CMFPlone.utils import getFSVersionTuple


if getFSVersionTuple() > (5, ):
    IS_PLONE_5 = True
else:
    IS_PLONE_5 = False


INDEXES = (("documentDate", "DateIndex"),)
