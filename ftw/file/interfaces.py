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


class IFilePreviewActionsCollector(Interface):
    """Adapter interface to generate an actions-listing in the file_preview-view
    """

    def get_actions(actions_to_list=[]):
        """Returns a dict with actions.

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
    """Adapter interface to generate the history in the file_preview-view
    """

    def get_journal():
        """Returns the versionhistory in a dict.
        """


class IFilePreviewFileInfoCollector(Interface):
    """Adapter interface to generate filedata-listing in the file_preview-view
    """

    def get_infos():
        """Returns a dict with fileinfos.

         An fileinfo looks like this:

            {
                'leftcolumn': 'Filename:',
                'rightcolumn': 'wonder.png',
            }

        """
