from Acquisition import aq_inner, aq_parent
from plone.app.contentrules.handlers import execute


def downloaded(event):
    """When a file is downloaded, execute rules assigned to its parent
    """
    execute(aq_parent(aq_inner(event.object)), event)
