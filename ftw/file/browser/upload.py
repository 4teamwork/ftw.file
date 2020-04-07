import json
import transaction

from Acquisition import aq_inner
from Acquisition import aq_parent
from Acquisition import aq_base
from ftw.file.utils import is_image
from plone import api
from plone.outputfilters.browser.resolveuid import uuidFor
from plone.restapi.exceptions import DeserializationError
from plone.restapi.interfaces import IDeserializeFromJson
from Products.CMFCore.interfaces._content import IFolderish
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from Products.TinyMCE.adapters.Upload import Upload
from zExceptions import BadRequest
from zope.component import queryMultiAdapter
from zope.i18n import translate
from zope.publisher.browser import BrowserView

from ftw.file import fileMessageFactory as _


class FileUpload(BrowserView):
    """View for handling drag-and-drop file replace"""

    def __call__(self):
        self.file = self.request.get('file')
        try:
            if not self.file:
                raise BadRequest('No content provided.')

            # Borrow code from plone.restapi which handles validation correctly
            deserializer = queryMultiAdapter((self.context, self.request), IDeserializeFromJson)
            if deserializer is None:
                self.request.response.setStatus(501)
                return json.dumps(dict(error=dict(
                    message="Cannot deserialize type {}".format(self.context.portal_type))
                ))

            # Will raise BadRequest if validation fails
            deserializer(data={'file': self.file, 'filename': self.file.filename})

            portal = api.portal.get()
            repository_tool = getToolByName(portal, 'portal_repository')

            if repository_tool.isVersionable(self.context):
                # TODO: This creates another entry in the history resulting
                # in two consecutive history entries.
                repository_tool.save(
                    self.context,
                    comment=translate(_('File replaced with Drag & Drop.'),
                                      context=self.request)
                )
        except BadRequest as br:
            transaction.doom()
            # Show validation failures on next page (file_view)
            if type(br.message) in (list, tuple):
                errors = br.message
                for msg in errors:
                    IStatusMessage(self.request).add(msg['message'], 'error')
            else:
                errors = [{'message': br.message}]
                IStatusMessage(self.request).add(br.message, 'error')

            self.request.response.setStatus(400)
            retval = {'success': False, 'errors': errors}
            self.request.response.setBody(retval, lock=True)
            return json.dumps(retval)
        else:
            # Note: deserializer has handled notify for ObjectEditedEvent
            return json.dumps({'success': True})


class TinyMCEFileUpload(Upload):

    def upload(self):
        """Adds uploaded file.

        Required params: uploadfile, uploadtitle, uploaddescription
        """
        context = aq_inner(self.context)
        self.request = context.REQUEST
        if not IFolderish.providedBy(context):
            context = aq_parent(context)

        request = context.REQUEST
        utility = getToolByName(context, 'portal_tinymce')

        id_ = request['uploadfile'].filename
        content_type = request['uploadfile'].headers["Content-Type"]
        # check if container is ready to store images
        if self.is_temporary(context):
            return self.errorMessage(
                translate(_('Please save the object first'
                            ' to enable image upload.'),
                          context=self.request))

        # check mime type to make sure an image is uploaded
        if not is_image(content_type):
            return self.errorMessage(
                translate(_('Only image upload allowed.'),
                          context=self.request))

        # Permission checks based on code by Danny Bloemendaal

        # 1) check if the current user has permissions to add stuff
        if not context.portal_membership.checkPermission(
            'Add portal content', context):
            return self.errorMessage(
                "You do not have permission to upload files in this folder")

        # 2) check image types uploadable in folder.
        #    priority is to content_type_registry image type
        allowed_types = [t.id for t in context.getAllowedTypes()]
        tiny_image_types = utility.imageobjects.split('\n')
        uploadable_types = []
        for typename in tiny_image_types:
            if typename in allowed_types:
                uploadable_types.append(typename)

        # Get an unused filename without path
        id_ = self.cleanupFilename(id_)

        for metatype in uploadable_types:
            try:
                newid = context.invokeFactory(type_name=metatype, id=id_)
                if newid is None or newid == '':
                    newid = id_
                break
            except ValueError:
                continue
            except BadRequest:
                return self.errorMessage(
                    translate(_("Bad filename, please rename."),
                              context=self.request))
        else:
            return self.errorMessage(translate(
                _("Not allowed to upload a file of this type to this folder"),
                context=self.request))

        obj = getattr(context, newid, None)
        if not obj:
            return self.errorMessage("Could not upload the file")

        # Update fields
        # Borrow code from plone.restapi which handles validation correctly
        try:
            deserializer = queryMultiAdapter((obj, self.request), IDeserializeFromJson)
            if deserializer is None:
                return self.errorMessage("Cannot deserialize type {}".format(obj.portal_type))

            try:
                uploaded_file = request['uploadfile']
                field_data = {
                    'file': uploaded_file,
                    'filename': uploaded_file.filename,
                    'title': request['uploadtitle'] or uploaded_file.filename,
                    'description': request['uploaddescription']
                }
                # Will raise BadRequest if validation fails
                # it also looks after notify(ObjectInitializedEvent ...)
                deserializer(data=field_data, validate_all=True, create=True)
            except DeserializationError as e:
                return self.errorMessage("DeserializationError: {}".format(str(e)))
        except BadRequest as br:
            transaction.doom()
            if type(br.message) in (list, tuple):
                # Multiple errors are so unlikely (and hard to test) that we
                # just return the first error
                error = br.message[0]['message']
            else:
                error = br.message
            return self.errorMessage(error)

        obj.reindexObject()
        folder = obj.aq_parent.absolute_url()

        if utility.link_using_uids:
            path = "resolveuid/%s" % (uuidFor(obj))
        else:
            path = obj.absolute_url()
        return self.okMessage(path, folder)

    def is_temporary(self, obj, checkId=True):
        """Checks, whether an object is a temporary object (means it's in the
        `portal_factory`) or has no acquisition chain set up.
        Source: http://svn.plone.org/svn/collective/collective.indexing
        /trunk/collective/indexing/subscribers.py
        """
        parent = aq_parent(aq_inner(obj))
        if parent is None:
            return True
        if checkId and getattr(obj, 'getId', None):
            if getattr(aq_base(parent), obj.getId(), None) is None:
                return True
        isTemporary = getattr(obj, 'isTemporary', None)
        if isTemporary is not None:
            try:
                if obj.isTemporary():
                    return True
            except TypeError:
                # `isTemporary` on the `FactoryTool` expects 2 args
                return True
        return False
