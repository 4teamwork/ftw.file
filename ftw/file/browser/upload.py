import json

from Acquisition import aq_inner
from Acquisition import aq_parent
from ftw.file.content.file import File
from plone import api
from plone.app.uuid.utils import uuidToObject
from plone.outputfilters.browser.resolveuid import uuidFor
from Products.CMFCore.interfaces._content import IFolderish
from Products.CMFCore.utils import getToolByName
from Products.TinyMCE.adapters.Upload import Upload
from zExceptions import BadRequest
from zope.event import notify
from zope.i18n import translate
from zope.lifecycleevent import ObjectModifiedEvent
from zope.publisher.browser import BrowserView

from ftw.file import fileMessageFactory as _

import pkg_resources
try:
    pkg_resources.get_distribution('plone.dexterity')
except pkg_resources.DistributionNotFound:
    HAS_DEXTERITY = False
else:
    HAS_DEXTERITY = True
    from plone.dexterity.interfaces import IDexterityContent


class FileUpload(BrowserView):
    """View for handling drag-and-drop file replace"""

    def __call__(self):
        self.file = self.request.get('file')
        if not self.file:
            raise BadRequest('No content provided.')

        self.filename = self.file.filename
        self.context.update(file=self.file, originFilename=self.filename)

        portal = api.portal.get()
        repository_tool = getToolByName(portal, 'portal_repository')

        if repository_tool.isVersionable(self.context):
            # TODO: This creates another entry in the history resulting in two consecutive history entries.
            repository_tool.save(
                self.context,
                comment=translate(_('File replaced with Drag & Drop.'),
                                  context=self.request)
            )

        notify(ObjectModifiedEvent(self.context))
        return json.dumps({'success': True})


class TinyMCEFileUpload(Upload):

    def okMessage(self, path, folder):
        ret = super(TinyMCEFileUpload, self).okMessage(path, folder)

        obj = uuidToObject(path.split('/')[1])
        if (obj.Title() == ''):
            obj.setTitle(obj.getFilename())

        return ret

    def upload(self):
        """Adds uploaded file.

        Required params: uploadfile, uploadtitle, uploaddescription
        """
        context = aq_inner(self.context)
        if not IFolderish.providedBy(context):
            context = aq_parent(context)

        request = context.REQUEST
        ctr_tool = getToolByName(context, 'content_type_registry')
        utility = getToolByName(context, 'portal_tinymce')

        id = request['uploadfile'].filename
        content_type = request['uploadfile'].headers["Content-Type"]
        typename = ctr_tool.findTypeName(id, content_type, "")

        # Permission checks based on code by Danny Bloemendaal

        # 1) check if the current user has permissions to add stuff
        if not context.portal_membership.checkPermission(
            'Add portal content', context):
            return self.errorMessage(
                "You do not have permission to upload files in this folder")

        # 2) check image types uploadable in folder.
        #    priority is to content_type_registry image type
        allowed_types = [t.id for t in context.getAllowedTypes()]
        if typename in allowed_types:
            uploadable_types = [typename]
        else:
            uploadable_types = []

        if content_type.split('/')[0] == 'image':
            image_portal_types = utility.imageobjects.split('\n')
            uploadable_types += [t for t in image_portal_types
                                    if t in allowed_types
                                       and t not in uploadable_types]

        # Get an unused filename without path
        id = self.cleanupFilename(id)

        for metatype in uploadable_types:
            try:
                newid = context.invokeFactory(type_name=metatype, id=id)
                if newid is None or newid == '':
                    newid = id
                break
            except ValueError:
                continue
            except BadRequest:
                return self.errorMessage(_("Bad filename, please rename."))
        else:
            return self.errorMessage(
                _("Not allowed to upload a file of this type to this folder"))

        obj = getattr(context, newid, None)

        # Set title + description.
        # Attempt to use Archetypes mutator if there is one, in case it uses
        # a custom storage
        title = request['uploadtitle']
        description = request['uploaddescription']

        if title:
            try:
                obj.setTitle(title)
            except AttributeError:
                obj.title = title

        if description:
            try:
                obj.setDescription(description)
            except AttributeError:
                obj.description = description

        if Upload.HAS_DEXTERITY and IDexterityContent.providedBy(obj):
            if not self.setDexterityImage(obj):
                return self.errorMessage(
                    _("The content-type '%s' has no image-field!" % metatype))
        else:
            # set primary field
            pf = obj.getPrimaryField()
            pf.set(obj, request['uploadfile'])

        if not obj:
            return self.errorMessage("Could not upload the file")

        obj.reindexObject()
        folder = obj.aq_parent.absolute_url()

        if utility.link_using_uids:
            path = "resolveuid/%s" % (uuidFor(obj))
        else:
            path = obj.absolute_url()
        return self.okMessage(path, folder)
