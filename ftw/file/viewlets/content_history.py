from Acquisition import aq_inner
from plone.app.layout.viewlets import content
from plone.app.layout.viewlets.content import ContentHistoryView
from plone.batching.batch import Batch
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFPlone.utils import log
from Products.CMFPlone import PloneMessageFactory as _
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

    @property
    def batch_size(self):
        return 10

    def history_batch(self):
        if 'b_start' in self.context.REQUEST.form:
            b_start = self.context.REQUEST.form['b_start']
        else:
            b_start = 0

        history = ContentHistoryView(self.context, self.context.REQUEST).fullHistory()
        if not history:
            return False

        batch = Batch(history, size=self.batch_size, start=b_start)
        return batch
