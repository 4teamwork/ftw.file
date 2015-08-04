from ftw.file.browser.file_view import FileView


class BumblebeeFileView(FileView):
    """
    """

    def file_preview(self):
        view = self.context.restrictedTraverse('@@file_preview')
        return view(
            actions_list=[
                'open_pdf',
                'download_original',
                'open_in_overlay',
                'edit',
                'external_edit',
                'delete'])
