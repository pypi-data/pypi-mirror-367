import pytest
from keydev_reports.report_tools.base_editor import BaseEditor


class TestBaseEditor:
    def test_init(self):
        editor = BaseEditor(file_name='test.xlsx')
        assert editor.file_name == 'test.xlsx'
        assert editor.output is not None
        assert editor.book is None

    def test_get_search_text(self):
        search_text = 'example'
        expected_result = '${example}'
        assert BaseEditor.get_search_text(search_text) == expected_result

    def test_get_filepath(self):
        editor = BaseEditor(file_name='test.xlsx')
        assert editor.get_filepath() == 'test.xlsx'

    def test_save(self):
        editor = BaseEditor(file_name='test.xlsx')
        with pytest.raises(AttributeError):
            editor.save()