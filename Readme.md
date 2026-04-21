# Headstrong Website - reads Markdown files but ships HTML!

## Overview

I keep my notes in markdown files, and my notes can be everything from a shopping list to a projects full documentation, embedded images, everything. 
I wanted a website that rendered these directly as HTML for the sites content pages.
I'm also more than content for these pages to be immediately visible on the site as soon as they appear in the markdown folder. No 'content moderation', immediately display the changes.
Finally, (and this one was the gotcha), I don't see the point in converting these files from markdown to HTML because markdown essentially IS HTML.

So that lead me to what seems obvious to me, to have a templating engine that takes in markdown files, renders them to HTML piped into a edfault main HTML template for styling.

## Detail

This repo has the main Python code thats using Flask as the main web engine. It uses Gunicorn as the larger engine to support a more productionised setup.
Finally it also has a dockerfile and this creates an image that then be used in a containerised environment.

The external markdown directory is bound to the container as a read-only mount point:
```bash
podman run -p 5000:5000 -v /home/User/Folder/Markdown/:/app/markdown:ro headstrong-site
```
