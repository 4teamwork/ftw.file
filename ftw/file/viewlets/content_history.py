from Acquisition import aq_inner
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.utils import getToolByName
from Products.CMFEditions.Permissions import AccessPreviousVersions
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.utils import log
from plone.app.layout.viewlets import content
from plone.batching.batch import Batch
from plone.protect.authenticator import createToken
import AccessControl
import logging


class ContentHistoryViewlet(content.ContentHistoryViewlet):
    """ History viewlet for ftw.file
    """

    def show_viewlet(self):
        """ Permission Access previous versions is required"""
        if _checkPermission('CMFEditions: Access previous versions',
                            self.context):
            return True
        return False

    def workflowHistory(self, complete=False):
        """Return workflow history of this context.

        Taken from plone_scripts/getWorkflowHistory.py

        Do not check for 'Request review'
        """
        context = aq_inner(self.context)
        # check if the current user has the proper permissions
        if not _checkPermission('CMFEditions: Access previous versions',
                                context):
            return []

        workflow = getToolByName(context, 'portal_workflow')
        membership = getToolByName(context, 'portal_membership')

        review_history = []

        try:
            # get total history
            # Change SecurityManager
            _old_security_manager = AccessControl.getSecurityManager()
            _new_user = AccessControl.SecurityManagement.SpecialUsers.system
            AccessControl.SecurityManagement.newSecurityManager(
                context.REQUEST,
                _new_user)

            try:
                review_history = workflow.getInfoFor(context, 'review_history')
            except:
                AccessControl.SecurityManagement.setSecurityManager(
                    _old_security_manager)
                raise
            else:
                AccessControl.SecurityManagement.setSecurityManager(
                    _old_security_manager)

            if not complete:
                # filter out automatic transitions.
                review_history = [r for r in review_history if r['action']]
            else:
                review_history = list(review_history)

            portal_type = context.portal_type
            anon = _(u'label_anonymous_user', default=u'Anonymous User')

            for r in review_history:
                r['type'] = 'workflow'
                r['transition_title'] = workflow.getTitleForTransitionOnType(
                    r['action'], portal_type)
                actorid = r['actor']
                r['actorid'] = actorid
                if actorid is None:
                    # action performed by an anonymous user
                    r['actor'] = {'username': anon, 'fullname': anon}
                    r['actor_home'] = ''
                else:
                    r['actor'] = membership.getMemberInfo(actorid)
                    if r['actor'] is not None:
                        r['actor_home'] = \
                            self.navigation_root_url + '/author/' + actorid
                    else:
                        # member info is not available
                        # the user was probably deleted
                        r['actor_home'] = ''
            review_history.reverse()

        except WorkflowException:
            log('plone.app.layout.viewlets.content: '
                '%s has no associated workflow' % context.absolute_url(),
                severity=logging.DEBUG)

        return review_history

    def revisionHistory(self):
        context = aq_inner(self.context)
        if not _checkPermission(AccessPreviousVersions, context):
            return []

        rt = getToolByName(context, "portal_repository", None)
        if rt is None or not rt.isVersionable(context):
            return []

        context_url = context.absolute_url()
        history = rt.getHistoryMetadata(context)
        portal_diff = getToolByName(context, "portal_diff", None)
        can_diff = portal_diff is not None \
            and len(portal_diff.getDiffForPortalType(context.portal_type)) > 0
        can_revert = _checkPermission(
            'CMFEditions: Revert to previous versions', context)

        def morphVersionDataToHistoryFormat(vdata, version_id):
            meta = vdata["metadata"]["sys_metadata"]
            userid = meta["principal"]
            token = createToken()
            preview_url = \
                "%s/versions_history_form?version_id=%s&_authenticator=%s#version_preview" % (  # noqa
                    context_url,
                    version_id,
                    token
                )

            filename = vdata['metadata'].get('app_metadata', {}).get('filename')
            download_url = ''
            if filename:
                download_url = u'{}/@@download-version?version_id={}&filename={}&_authenticator={}'.format(
                    context_url,
                    version_id,
                    filename,
                    token,
                )

            info = dict(
                type='versioning',
                action=_(u"Edited"),
                transition_title=_(u"Edited"),
                actorid=userid,
                time=meta["timestamp"],
                comments=meta['comment'],
                version_id=version_id,
                preview_url=preview_url,
                download_url=download_url,
                filename=filename
            )
            if can_diff:
                if version_id > 0:
                    info["diff_previous_url"] = (
                        "%s/@@history?one=%s&two=%s&_authenticator=%s" %
                        (context_url, version_id, version_id - 1, token)
                    )
                if not rt.isUpToDate(context, version_id):
                    info["diff_current_url"] = (
                        "%s/@@history?one=current&two=%s&_authenticator=%s" %
                        (context_url, version_id, token)
                    )
            if can_revert:
                info["revert_url"] = "%s/revertversion" % context_url
            else:
                info["revert_url"] = None
            info.update(self.getUserInfo(userid))
            return info

        # History may be an empty list
        if not history:
            return history

        version_history = []
        retrieve = history.retrieve
        getId = history.getVersionId
        # Count backwards from most recent to least recent
        for i in range(history.getLength(countPurged=False) - 1, -1, -1):
            version_history.append(
                morphVersionDataToHistoryFormat(retrieve(i, countPurged=False),
                                                getId(i, countPurged=False)))

        return version_history

    @property
    def batch_size(self):
        return 10

    def history_batch(self):
        if 'b_start' in self.context.REQUEST.form:
            b_start = self.context.REQUEST.form['b_start']
        else:
            b_start = 0

        history = self.fullHistory()
        if not history:
            return False

        batch = Batch(history, size=self.batch_size, start=b_start)
        return batch
