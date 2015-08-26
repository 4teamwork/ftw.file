"""Main product initializer
"""
from Products.Archetypes import atapi
from Products.CMFCore.utils import ContentInit
from ftw.file import config
from zope.i18nmessageid import MessageFactory

fileMessageFactory = MessageFactory('ftw.file')


def initialize(context):
    """Initializer called when used as a Zope 2 product."""

    # Retrieve the content types that have been registered with Archetypes.
    content_types, constructors, ftis = atapi.process_types(
        atapi.listTypes(config.PROJECTNAME),
        config.PROJECTNAME)

    # Now initialize all these content types.
    for atype, constructor in zip(content_types, constructors):
        ContentInit('%s: %s' % (config.PROJECTNAME, atype.portal_type),
                    content_types=(atype, ),
                    permission=config.ADD_PERMISSIONS[atype.portal_type],
                    extra_constructors=(constructor, ),
                    ).initialize(context)
