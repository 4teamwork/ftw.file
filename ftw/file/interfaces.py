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

    def get_actions(actions_to_list=[]):
        """Returns a dict with actions defined in it actions_to_list.

        Only actions in this list will be returned from the adapter.
        You can set the sort order or add or remove actions.
        The action-names listed in this attribute are without
        the prefix _action_.

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


class IFilePreviewJournal(Interface):
    """
    """

    def get_journal():
        """
        """
