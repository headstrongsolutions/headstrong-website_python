from os import path, chdir, walk, getenv
from pathlib import Path
import urllib.request
import json
from datetime import datetime
from glob import glob
from flask import Flask, render_template, send_file, abort
from MarkdownToHTML import MarkdownToHTML
app = Flask(__name__)
year = datetime.now().year

markdown_type = ".md"
media_type_patterns=(
   "*.svg",
   "*.gif",
   "*.png",
   "*.jpg",
   "*.jpeg",
   "*.txt"
)
media_types=[
   ".svg",
   ".gif",
   ".png",
   ".jpg",
   ".jpeg",
   ".txt"
]

# Helper functions

def get_default_path():
   dir_path = path.dirname(path.realpath(__file__))
   return path.join(dir_path, 'markdown')

def get_main_sections():
   return next(walk(get_default_path()))[1]

def get_url_portions(first: str, second: str, third: str, fourth: str) -> (str, str):
   """get_url_portions(first: str, second: str, third: str, fourth: str)
      Returns a tuple containing the filename and the full url of the accumulated portions

      first/second/third/fourth: nullable strings containing url portions, e.g. "/Project/PeaWhistle/Images/top.jpg" 
      Returns (filename: str, full_path: str):
               e.g.  "/Project/PeaWhistle/Images/top.jpg" -> ("top.jpg", "/Project/PeaWhistle/Images/")
                     "/Photos/middle_earth5.jpg" -> ("middle_earth.jpg", "/Photos/")
   """
   filename     = ""
   full_path    = ""
   if first:
      filename  =  "/" + first  + "/"
      full_path =  f"/"
   if second:
      filename  =  "/" + second + "/"
      full_path =  f"/{first}/"
   if third:
      filename  =  "/" + third  + "/"
      full_path =  f"/{first}/{second}/"
   if fourth:
      filename  =  "/" + fourth + "/"
      full_path =  f"/{first}/{second}/{third}/"

   return (filename.strip("/"), full_path)

def render_markdown_file(path:str, filename: str)->str:
   """markdown_filelist(title:str, path:str, type:str)
      Returns a markdown formatted page listing the contents of a directory

      path: string containing a path to a directory of the markdown file
      filename: string containing the filename of the markdown file
   """
   markdownToHTML = MarkdownToHTML(path)
   markdownToHTML.set_markdown_filepath(f"{path}{filename}")
   markdownToHTML.convert_markdown_file()
   return markdownToHTML.output

def markdown_filelist(page_name:str, path:str, type:str):
   """markdown_filelist(title:str, path:str, type:str)
      Returns a markdown formatted page listing the contents of a directory

      title: string containing text to displa yas the page title
      path: string containing a path to a directory to list the contents of
      type: string, (either 'media' or 'markdown') to select what filetypes to list
   """
   markdown_output = f"# {page_name}\n"
   filenames = []
   if type == "markdown":
      for markdown_file in glob(f"{path}/*{markdown_type}"):
         markdown_name = markdown_file.replace(path, "")
         markdown_name = markdown_name.replace({markdown_type},"")
         filenames.append(f" - [{markdown_name}]({path}/{markdown_name})")
      markdown_output += "".join(filenames)
   elif type == "media":
      folder = Path(path)
      patterns = passthrough_media_types
      media_files = [f for f in folder.iterdir() if any(f.match(p) for p in patterns)]
      for media_file in media_files:
         markdown_name = markdown_file.replace(path, "")
         for media_type in media_types:
            markdown_name = markdown_name.replace(media_type,"")
         filenames.append(f" - [{markdown_name}]({markdown_path}/{markdown_name})")
      markdown_output += "".join(filenames)
   return markdown_output

# Generic routes
@app.route('/')
def home():
   return render_template('index.html', year = year, sections = get_main_sections())

@app.route('/contact')
def contact():
   return render_template('contact.html', year = year, sections = get_main_sections())

@app.route('/privacy')
def privacy():
      return render_template('privacy.html', year = year, sections = get_main_sections())


# List content pages
@app.route('/pages/<first>/')
def content_page_overloaded_first(first):
   return content_page(first=first, second=None, third=None, fourth=None)

@app.route('/pages/<first>/<second>/')
def content_page_overloaded_second(first, second):
   return content_page(first=first, second=second, third=None, fourth=None)

@app.route('/pages/<first>/<second>/<third>/')
def content_page_overloaded_third(first, second, third):
   return content_page(first=first, second=second, third=third, fourth=None)

@app.route('/pages/<foldername>/<subfoldername>/<filename>/<mediafilename>/')
def content_page(foldername, subfoldername, filename, mediafilename):
   get_filename


# Markdown pages
@app.route('/pages/<first>')
def markdown_page_overloaded_first(first):
   return markdown_page(first=first, second=None, third=None, fourth=None)

@app.route('/pages/<first>/<second>')
def markdown_page_overloaded_second(first, second):
   return markdown_page(first=first, second=second, third=None, fourth=None)

@app.route('/pages/<first>/<second>/<third>')
def markdown_page_overloaded_third(first, second, third):
   return markdown_page(first=first, second=second, third=third, fourth=None)

@app.route('/pages/<first>/<second>/<third>/<fourth>')
def markdown_page(first, second, third, fourth):
   default_path = get_default_path()
   (filename, full_path) = get_url_portions(first, second, third, fourth)
   if path.exists(f"{default_path}{full_path}{filename}"):
      if any(media_type in filename for media_type in media_types):
         return send_file(f"{default_path}{full_path}{filename}")
      if markdown_type in filename:
         
         markdown = render_markdown_file(f"{default_path}{full_path}", filename)
         return render_template('markdown_page.html', markdown=markdown, year = year, sections = get_main_sections())
   else:
      abort(404)

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
