from os import path, chdir, walk, getenv
import urllib.request
import json
from datetime import datetime
from glob import glob
from flask import Flask, render_template, send_file
from MarkdownToHTML import MarkdownToHTML
app = Flask(__name__)
year = datetime.now().year
passthrough_media_types=[
   ".svg",
   ".gif",
   ".png",
   ".jpg",
   ".jpeg",
   ".txt"
]
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
   mediafilename=None
   return markdown_page(
      foldername=foldername,
      subfoldername=subfoldername,
      filename=filename,
      mediafilename=mediafilename)

@app.route('/pages/<foldername>')
@app.route('/pages/<foldername>/')
def markdown_page_overloaded_foldername(foldername):
   subfoldername=None
   filename=None
   mediafilename=None
   return markdown_page(
      foldername=foldername,
      subfoldername=subfoldername,
      filename=filename,
      mediafilename=mediafilename)

@app.route('/pages/<foldername>/<subfoldername>')
@app.route('/pages/<foldername>/<subfoldername>/')
def markdown_page_overloaded_subfoldername(foldername, subfoldername):
   filename=None
   mediafilename=None
   return markdown_page(
      foldername=foldername,
      subfoldername=subfoldername,
      filename=filename,
      mediafilename=mediafilename)

@app.route('/pages/<foldername>/<subfoldername>/<filename>')
@app.route('/pages/<foldername>/<subfoldername>/<filename>/')
def markdown_page_overloaded_mediafilename(foldername, subfoldername, filename):
   mediafilename=None

   return markdown_page(
      foldername=foldername,
      subfoldername=subfoldername,
      filename=filename,
      mediafilename=mediafilename)

def markdown_filelist(page_name):
   markdown_output = f"# {page_name}\n"
   markdown_filenames = []
   path_exists = path.exists(full_markdown_path)
   if path_exists:
      # is there an index.md file in this dir?
      index_exists = path.exists(f"{full_markdown_path}/index.md")
      if index_exists:
      # if not generate a list of the md files in this folder to act as an index page
         markdownToHTML.set_markdown_filepath(f"{full_markdown_path}/index.md")
         markdownToHTML.convert_markdown_file()
      else:
         for markdown_file in glob(f"{full_markdown_path}/*.md"):
            markdown_name = markdown_file.replace(full_markdown_path, "")
            markdown_name = markdown_name.replace(".md","")
            markdown_name = markdown_name.strip("/")
            markdown_filenames.append(f" - [{markdown_name}]({markdown_path}/{markdown_name})")
         markdown_output += "".join(markdown_filenames)
   return markdown_output

def create_filepath_routes(foldername, subfoldername, filename, mediafilename):
   full_filepath = get_default_path()
   markdown_path = "/pages/"
   full_markdown_path = full_filepath

   if foldername and not subfoldername and not filename and not mediafilename:
      markdown_path += f"{foldername}"
      full_markdown_path += f"/{foldername}"
   elif foldername and subfoldername and not filename and not mediafilename:
      full_filepath += f"/{foldername}"
      markdown_path += f"{foldername}/{subfoldername}"
      full_markdown_path += f"/{foldername}/{subfoldername}"
   elif foldername and subfoldername and filename and not mediafilename:
      full_filepath += f"/{foldername}/{subfoldername}"
      markdown_path += f"{foldername}/{subfoldername}/{filename}"
      full_markdown_path += f"/{foldername}/{subfoldername}/{filename}"
   elif foldername and subfoldername and filename and mediafilename:
      full_filepath += f"/{foldername}/{subfoldername}/{filename}"
      markdown_path += f"{foldername}/{subfoldername}/{filename}/{mediafilename}"
      full_markdown_path += f"/{foldername}/{subfoldername}/{filename}/{mediafilename}"
   
   return (full_filepath, markdown_path, full_markdown_path)

@app.route('/pages/<foldername>/<subfoldername>/<filename>/<mediafilename>')
@app.route('/pages/<foldername>/<subfoldername>/<filename>/<mediafilename>/')
def markdown_page(foldername, subfoldername, filename, mediafilename):

   (full_filepath, markdown_path, full_markdown_path) = create_filepath_routes(foldername, subfoldername, filename, mediafilename)

   full_markdown_path = full_markdown_path.replace(".md","")
   # return media request with file asap
   if any(ext in full_markdown_path for ext in passthrough_media_types):
      if path.exists(full_markdown_path):
         return send_file(full_markdown_path)
   markdownToHTML = MarkdownToHTML(default_path = full_filepath)

   file_exists = path.exists(f"{full_markdown_path}.md")   
   if file_exists:
      markdownToHTML.set_markdown_filepath(f"{full_markdown_path}.md")
      markdownToHTML.convert_markdown_file()
   else:
      markdown_output = markdown_filelist("Placeholder for page name")
   markdown = markdownToHTML.output
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