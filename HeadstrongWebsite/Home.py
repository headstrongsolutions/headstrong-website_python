from os import path, chdir, walk, getenv
import urllib.request
import json
from datetime import datetime
from glob import glob
from flask import Flask, render_template
from MarkdownToHTML import MarkdownToHTML
app = Flask(__name__)
year = datetime.now().year
def get_default_path():
   dir_path = path.dirname(path.realpath(__file__))
   return path.join(dir_path, 'markdown')

def get_main_sections():
   return next(walk(get_default_path()))[1]

@app.route('/')
def home():
   return render_template('index.html', year = year, sections = get_main_sections())

@app.route('/contact')
def contact():
   return render_template('contact.html', year = year, sections = get_main_sections())

@app.route('/privacy')
def privacy():
      return render_template('privacy.html', year = year, sections = get_main_sections())



@app.route('/pages/')
def markdown_page_overloaded_page():
   foldername = None
   subfoldername=None
   filename=None
   return markdown_page(
      foldername=foldername,
      subfoldername=subfoldername,
      filename=filename)

@app.route('/pages/<foldername>')
@app.route('/pages/<foldername>/')
def markdown_page_overloaded_foldername(foldername):
   subfoldername=None
   filename=None
   return markdown_page(
      foldername=foldername,
      subfoldername=subfoldername,
      filename=filename)

@app.route('/pages/<foldername>/<subfoldername>')
@app.route('/pages/<foldername>/<subfoldername>/')
def markdown_page_overloaded_subfoldername(foldername, subfoldername):
   filename=None

   return markdown_page(
      foldername=foldername,
      subfoldername=subfoldername,
      filename=filename)

@app.route('/pages/<foldername>/<subfoldername>/<filename>')
@app.route('/pages/<foldername>/<subfoldername>/<filename>/')
def markdown_page(foldername, subfoldername, filename):

   full_filepath = get_default_path()
   markdown_path = "/pages/"
   full_markdownpath = full_filepath

   if foldername and not subfoldername and not filename:
      markdown_path += f"{foldername}"
      full_markdownpath += f"/{foldername}"
   elif foldername and subfoldername and not filename:
      full_filepath += f"/{foldername}"
      markdown_path += f"{foldername}/{subfoldername}"
      full_markdownpath += f"/{foldername}/{subfoldername}"
   elif foldername and subfoldername and filename:
      full_filepath += f"/{foldername}/{subfoldername}"
      markdown_path += f"{foldername}/{subfoldername}/{filename}"
      full_markdownpath += f"/{foldername}/{subfoldername}/{filename}"

   markdownToHTML = MarkdownToHTML(default_path = full_filepath)
   
   file_exists = path.exists(f"{full_markdownpath}.md")   
   if file_exists:
      markdownToHTML.set_markdown_filepath(f"{full_markdownpath}.md")
      markdownToHTML.convert_markdown_file()
   else:
      markdown_output = "# List of things\n"
      markdown_filenames = []
      path_exists = path.exists(full_markdownpath)
      if path_exists:
         # is there an index.md file in this dir?
         index_exists = path.exists(f"{full_markdownpath}/index.md")
         if index_exists:
         # if not generate a list of the md files in this folder to act as an index page
            markdownToHTML.set_markdown_filepath(f"{full_markdownpath}/index.md")
            markdownToHTML.convert_markdown_file()
         else:
            for markdown_file in glob(f"{full_markdownpath}/*.md"):
               markdown_name = markdown_file.replace(full_markdownpath, "")
               markdown_name = markdown_name.replace(".md","")
               markdown_name = markdown_name.strip("/")
               markdown_filenames.append(f" - [{markdown_name}]({markdown_path}/{markdown_name})")
            markdown_output += "".join(markdown_filenames)
            markdownToHTML.convert_markdown_raw(markdown_output)
   markdown = markdownToHTML.output # BUG - For some reason output is empty...
   return render_template('markdown_page.html', markdown=markdown, year = year, sections = get_main_sections())

@app.route('/temps')
def temps():
   return render_template('temps.html', year = year, sections = get_main_sections())


@app.route('/api/get_temps')
def api_gettemps():
   gettemps_url = getenv("GETTEMPS_URL", default= None)
   temps = ""
   with urllib.request.urlopen(gettemps_url) as url_get:
      temps = json.loads(url_get.read())
   return temps

if __name__ == '__main__':
   app.run()