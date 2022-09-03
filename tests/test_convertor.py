import os 
import pytest
from HeadstrongWebsite.MarkdownToHTML import MarkdownToHTML

@pytest.fixture
def markdown_instance():
    '''Returns a MArkdownToHTML instance with a default path set to 'tests' folder'''
    dir_path = os.path.dirname(os.path.realpath(__file__))
    return MarkdownToHTML(default_path = dir_path)

def test_can_set_path(markdown_instance):
    assert markdown_instance.default_path is not None

def test_overwrite_default_path(markdown_instance):
    assert markdown_instance.default_path == os.path.dirname(os.path.realpath(__file__))
    up_one_level = os.path.dirname(os.path.realpath(__file__).replace('/tests', ''))
    markdown_instance.set_default_filepath(up_one_level)
    assert markdown_instance.default_path == up_one_level

def test_markdown_filepath(markdown_instance):
    assert markdown_instance.markdown_filename is None
    markdown_instance.set_markdown_filepath('markdown/README.md')
    assert markdown_instance.markdown_filename is not None

def test_markdown_HTML_output_not_empty(markdown_instance):
    assert markdown_instance.output_html() is None
    markdown_instance.set_markdown_filepath('markdown/README.md')
    markdown_instance.convert_markdown_file()
    assert markdown_instance.output_html() is not None