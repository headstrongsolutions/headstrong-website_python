import markdown
from os import path
import pathlib

"""
Markdown convertor for Headstrong Solutions website
"""

class MarkdownToHTML:
    
    def __init__(self, default_path: str):
        self.errors = []
        if self.check_path(default_path):
            self.default_path = default_path
        else:
            self.default_path = None
            self.errors.append("On Init default_path does not exist")
        self.markdown_filename = None
        self.output = None 

    def check_path(self, passed_path:str = None):
        path = None
        if passed_path:
            path = passed_path
        else:
            path = self.default_path
        return pathlib.Path(path)

    def set_default_filepath(self, default_path: str):
        try:
            self.default_path = default_path
        except(error):
            self.errors.append(f"Setting markdown default path from {default_path} caused the following error: {error}")

    
    def set_markdown_filepath(self, markdown_filename: str):
        try:
            self.markdown_filename = markdown_filename
        except(error):
            self.errors.append(f"Setting markdown file path from {markdown_filename} caused the following error: {error}")

    def markdown_file_exists(self, filename):
        return path.isfile(path.join(self.default_path, f"{filename}.md"))

    def convert_markdown_raw(self, text: str):
        self.output = markdown.markdown(text, extensions=['markdown_checklist.extension'])

    def convert_markdown_file(self):
        full_path = path.join(self.default_path, self.markdown_filename)
        if path.isfile(full_path):
            with open(full_path, 'r') as f:
                text = f.read()
                if text:
                    self.output = markdown.markdown(text, extensions=['markdown_checklist.extension'])
                    return True
                else:
                    self.errors.append(f"Converting {self.markdown_filename} returned an empty string, was this expected?")
                    return False
        else:
            self.errors.append("Unable to open file when converting markdown file")

    def output_html(self):
        return self.output
