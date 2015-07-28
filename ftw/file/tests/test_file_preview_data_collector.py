from ftw.file.browser.file_preview import FilePreviewCollector
from ftw.file.testing import FTW_FILE_BUMBLEBEE_FUNCTIONAL_TESTING
from unittest2 import TestCase


class TestFilePreviewActionsCollectorAdapter(TestCase):

    layer = FTW_FILE_BUMBLEBEE_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_collect_without_collection_to_list_returns_empty_list(self):
        collector = FilePreviewCollector(self.portal, object)

        self.assertEqual(
            [], collector(),
            'If no actions are defined in the actions_to_list-variable '
            'it should return an empty list')

    def test_collect_with_not_existing_function(self):
        collector = FilePreviewCollector(self.portal, object)

        self.assertEqual(
            [], collector(collector_list=['not-existing']),
            'If a function does not exists, it should be ignored '
            'by the collector')

    def test_do_not_collect_if_collectionfunction_returns_none(self):
        collector = FilePreviewCollector(self.portal, object)
        collector._data_testdata = lambda: {}

        self.assertEqual(
            [], collector(collector_list=['testdata']),
            'If a collector-functions returns none, it should '
            'be ignored by the collector')

    def test_collectorfunction_method_needs_a_data_prefix(self):
        collector = FilePreviewCollector(self.portal, object)
        collector.without_prefix = lambda: {'chuck': 'norris'}
        collector._data_with_prefix = lambda: {'chuck': 'norris'}

        self.assertEqual(
            [], collector(collector_list=['without_prefix']),
            'Each collectorfunction needs a prefix: "_data_". Otherwise, '
            'it will be ignored by the collector')

        self.assertEqual(
            [{'chuck': 'norris'}], collector(collector_list=['with_prefix']),
            'Functions with the prefix: "_data_" should be called from the '
            'collector. Please check the collector.')

    def test_collect_data_if_function_exists_and_it_returns_data(self):
        collector = FilePreviewCollector(self.portal, object)
        collector._data_testfunction = lambda: {'chuck': 'norris'}

        self.assertEqual(
            [{'chuck': 'norris'}], collector(collector_list=['testfunction']),
            'Functions with the prefix: "_data_" should be called from the '
            'collector. Please check the collector.')

    def test_collecting_data_in_order_of_collector_list_parameter(self):
        collector = FilePreviewCollector(self.portal, object)

        collector._data_test1 = lambda: {'url': 'test1'}
        collector._data_test2 = lambda: {'url': 'test2'}
        collector._data_test3 = lambda: {'url': 'test3'}

        self.assertEqual([
            {'url': 'test1'}, {'url': 'test3'}, {'url': 'test2'}],
            collector(collector_list=['test1', 'test3', 'test2']),
            'The collected data should be sorted like defined '
            'in the collector_list')
