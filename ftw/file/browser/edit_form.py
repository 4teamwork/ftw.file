from plone.dexterity.browser import edit


class EditForm(edit.DefaultEditForm):

    def applyChanges(self, data):

        if self.request.get('form.widgets.file.action') != u'nochange':
            data['filename_override'] = None

        super(EditForm, self).applyChanges(data)
