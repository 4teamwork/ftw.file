from Products.ATContentTypes.interfaces import IFileContent
from zope.component.interfaces import IObjectEvent
from zope.interface import Attribute
from zope.interface import Interface


class IFile(IFileContent):
    """File marker interface.
    """


class IFileDownloadedEvent(IObjectEvent):
    """An event fired when a file is downloaded"""

    context = Attribute("The file object that was downloaded")


class IFilePreviewActions(Interface):
    """Adapter interface to generate an actions-listing in the file_preview-view
    """

    actions_to_list = Attribute(
        """Only actions in this list will be returned from the adapter.
        You can override this attribute to change sort order or to add or
        remove actions.
        The action-names listed in this attribute are without
        the prefix _action_.""")

    def get_actions():
        """Returns a dict with actions defined in it.

        An action looks like this:

            {
                'url': 'www.google.ch',
                'target': '_top',
                'cssclass: 'fileLink',
                'text': 'Link to google',
                'image': {'src': '/img.jpg',
                          'title': 'Chuck',
                          'alt': 'Chuck Norris'}
            }
        """