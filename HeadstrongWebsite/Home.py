from os import path, chdir, walk, getenv, listdir
from pathlib import Path
import urllib.request
import json
from datetime import datetime
from glob import glob
from flask import Flask, render_template, send_file, abort
from MarkdownToHTML import MarkdownToHTML
app = Flask(__name__)
app.url_map.strict_slashes = False
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
               e.g.  "/Project/PeaWhistle/Images/top.jpg" -> ("top.jpg", 
                                                              "/Project/PeaWhistle/Images/", 
                                                              "/Project/PeaWhistle/Images/top.jpg")
                     "/Photos/middle_earth.jpg"           -> ("middle_earth.jpg",
                                                              "/Photos/",
                                                              "/Photos/middle_earth.jpg")
                     "/First/Second/Third/"               -> ("Third",
                                                              "/First/Second/",
                                                              "/First/Second/Third/")
   """
   filename     = "/"
   file_path    = ""
   full_path    = "/"
   if first:
      filename  =   first  + "/"
      file_path =  f"/"
      full_path +=  filename
   if second:
      filename  =  second + "/"
      file_path =  f"/{first}/"
      full_path +=  filename
   if third:
      filename  =  third  + "/"
      file_path =  f"/{first}/{second}/"
      full_path +=  filename
   if fourth:
      filename  =  fourth + "/"
      file_path =  f"/{first}/{second}/{third}/"
      full_path +=  filename

   return (filename.strip("/"), file_path, full_path)

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

def render_markdown_raw(path:str, content: str)->str:
   """render_markdown_raw(path:str, content:str, type:str)
      Returns a HTML formatted string from markdown content

      path: string containing a path to a directory of markdown files
      content: string containing HTML content
   """
   markdownToHTML = MarkdownToHTML(path)
   markdownToHTML.convert_markdown_raw(content)
   return markdownToHTML.output

def markdown_filelist(full_path:str, type:str):
   """markdown_filelist(title:str, path:str, type:str)
      Returns a markdown formatted page listing the contents of a directory

      full_path: string containing a path to a directory to list the contents of
      type: string, (either 'media' or 'markdown' or 'directory') to select what to list
   """
   markdown_output = ""
   filenames = []
   if type == "markdown":
      default_path = get_default_path()
      markdown_files = glob(f"{default_path}{full_path}*{markdown_type}")
      if len(markdown_files) > 0:
         for markdown_file in markdown_files:
            markdown_name = markdown_file.replace(f"{default_path}{full_path}", "")
            filenames.append(f" - [{markdown_name}](/pages{full_path}{markdown_name})\n")
      else:
         filenames.append("No markdown files found\n")
      markdown_output += "".join(filenames)
   elif type == "media":
      folder = Path(f"{get_default_path()}/{full_path}")
      patterns = media_type_patterns
      media_files = [f for f in folder.iterdir() if any(f.match(p) for p in patterns)]
      if len(media_types) > 0:
         for media_file in media_files:
            for media_type in media_types:
               if media_type == media_file.suffix:
                  filenames.append(f" - [{media_file.name}](/pages{full_path}{media_file.name})\n")
      else:
         filenames.append("No media files found\n")
      markdown_output += "".join(filenames)
   elif type == "directory":
      base_directory = Path(f"{get_default_path()}/{full_path}")
      directories = listdir(base_directory)                       # BUG - this threw a directory not found in production when trying to open a .md file
      for file in directories:
         directory = path.join(base_directory, file)
         if path.isdir(directory):
            directory_name = directory.replace(str(base_directory),"").strip("/")
            filenames.append(f" - [{directory_name}/](/pages{full_path}{directory_name}/)\n")
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

@app.route('/pages/<first>/<second>/<third>/<fourth>/')
def content_page(first, second, third, fourth):
   (directory_name, file_path, full_path) = get_url_portions(first, second, third, fourth)
   content  = f"# {directory_name}\n"
   if file_path != "/":
      content += f"[up a level](/pages{file_path})\n"
   content += "### Folders\n"
   content += markdown_filelist(full_path, "directory")
   content += "### Markdown Files\n"
   content += markdown_filelist(full_path, "markdown")
   content += "### Media Files\n"
   content += markdown_filelist(full_path, "media")
   markdownToHTML = MarkdownToHTML(full_path)
   markdown = render_markdown_raw(full_path, content)
   return render_template('markdown_page.html', markdown=markdown, year = year, sections = get_main_sections())

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
   (filename, file_path, full_path) = get_url_portions(first, second, third, fourth)
   if path.exists(f"{default_path}{file_path}{filename}"):
      if any(media_type in filename for media_type in media_types):
         return send_file(f"{default_path}{file_path}{filename}")
      if markdown_type in filename:
         
         markdown = render_markdown_file(f"{default_path}{file_path}", filename)
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
