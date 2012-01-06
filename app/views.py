from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from google.appengine.ext import db

from app.models import *

import os, sys, datetime, copy, logging, settings


# Change everything in this class! Makes things pretty fast and easy
# so the basic info about the site is ubiquitous. 
class globvars():
  pages = [
      {'name':'Home', 'url':'../../'}, # add pages here
    ]
  proj_name = "DecisionCandy HackPack" # change this!
  founders = [
    {'name':'Alex Rattray', #obviously, not you. 
       'email':'rattray@wharton.upenn.edu',
       'url':'http://alexrattray.com',
       'blurb':'I\'m Alex. I like webdev and most things Seattle.',
       'picture':''}, #to self-host, put images in /front-end/media/images 
    {'name':'Greg Terrono', #also not you. 
       'email':'terronogr@seas.upenn.edu',
       'url':'',
       'blurb':'I\'m Greg. I like webdev and most things Boston. (??)',
       'picture':'http://ia.media-imdb.com/images/M/MV5BMTk2MzU4ODA4NV5BMl5BanBnXkFtZTcwNzI3NDk0NA@@._V1._SX214_CR0,0,214,314_.jpg'},
    ]
  proj_description = "A quick and dirty package of Django on Google App Engine running Python 2.7 with HTML5 Boilerplate and Twitter Bootstrap."
  context = {
      'pages': pages,
      'proj_name': proj_name,
      'founders': founders,
      'proj_description': proj_description,
      }
  
def index(request):
  gv = globvars
  context = {
    'thispage':'Home'
      }
  context = dict(context, **gv.context) #combines the 'local' context with the 'global' context
  return render_to_response('index.html', context)
