from django import forms
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.core import serializers
from django.utils import simplejson
from django.template import RequestContext
from django.contrib.auth.models import User
from django.contrib import auth
from google.appengine.api import images 
from google.appengine.ext import db
from django.template.defaultfilters import slugify

from app.models import *

import os, sys, datetime, copy, logging, settings


# Change everything in this! Makes things pretty fast and easy
# so the basic info about the site is ubiquitous. 
class globvars():
  pages = [
      {'name':'Home', 'url':'../../'}, #Make a "the elements" section
      {'name':'About', 'url':'../../about'}, #Make a Contact section here
      {'name':'More Resources', 'url':'../../resources'},
      {'name':'Setup Tutorial', 'url':'../../tutorial'},
      {'name':'Sample Guestbook App', 'url':'../../guestbook'},
    ]
  proj_name = "DecisionCandy HackPack"
  founders = [
    {'name':'Alex Rattray',
       'email':'rattray@wharton.upenn.edu',
       'url':'http://alexrattray.com',
       'blurb':'I\'m Alex. I like webdev and most things Seattle.',
       'picture':'http://profile.ak.fbcdn.net/hprofile-ak-ash2/273392_515004220_1419119046_n.jpg'},
    {'name':'Greg Terrono',
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

def about(request):
  gv = globvars
  context = {
    'thispage':'About'
      }
  context = dict(context, **gv.context)
  return render_to_response('about.html', context)

def resources(request):
  gv = globvars
  context = {
    'thispage':'More Resources'
      }
  context = dict(context, **gv.context)
  return render_to_response('resources.html', context)

def tutorial(request):
  gv = globvars
  context = {
    'thispage':'Setup Tutorial'
      }
  context = dict(context, **gv.context)
  return render_to_response('tutorial.html', context)

def guestbook(request):
  gv = globvars
  context = {
    'thispage': 'Sample Guestbook App'
    }
  context = dict(context, **gv.context)
  return render_to_response('guestbook.html', context)

#######below this lies shit from dc

def image_handler(request, ID):
  project_name = str(project).replace('%20',' ')
  logging.warning(project_name)
  project = Project.objects.get(name=project_name)
  if project.images:
    headers = "Content-Type: image/png"
    if int(ID) == 0:
#      logging.warning("ID was zero")
      img = project.images.all()[0]
      the_image = img.full if size=='full' else img.medium
    else:
      img = project.images.get(id=int(ID))
      logging.info(size=='full')
      the_image = img.full if size=='full' else img.medium
    return HttpResponse(the_image, headers)



class SignUpForm(forms.Form):
  email = forms.EmailField(max_length=30)
  password = forms.CharField(widget=forms.PasswordInput, label="Your Password")
  name = forms.CharField(max_length=50, label="Publicly visible name")
  description = forms.CharField(widget=forms.Textarea)
  
def signup(request):
  if request.method == 'POST':
    form = SignUpForm(request.POST)
    if form.is_valid():
      email = form.cleaned_data['email']
      password = form.cleaned_data['password']
      username = email
      name = form.cleaned_data['name']
      description = form.cleaned_data['description']

      user = User.objects.create_user(username, email, password)
      user.save()
      
      client = Client(name=name, email=email, user=user, description=description)
      client.save()
      
      user = auth.authenticate(username=email, password=password)
      if user is not None:
        auth.login(request, user)
      return HttpResponseRedirect('/loggedin/')
  else:
    form = SignUpForm()
  return render_to_response('signup.html', {'form':form,}, context_instance = RequestContext(request))

class create_project(forms.Form):
  name = forms.CharField(max_length=100, label="Project Name")
  description = forms.CharField(widget=forms.Textarea, label="A description of your project")
  criteria = forms.CharField(max_length=100, label="Criteria (Which one ___?)")
  more_criteria = forms.CharField(widget=forms.Textarea, label="More Criteria (what else is important?)")

def myFileHandler(request):
  # logging.warning(request)
  if request.method == 'POST':
    for field_name in request.FILES:
      uploaded_file = request.FILES[field_name]
      logging.warning(uploaded_file)
      project = request.POST['project']
      new_image = Image()
      new_image.project = Project.objects.get(name=project)
      f = uploaded_file.read()
      new_image.full = db.Blob(f)
      img = images.Image(f)
      img.resize(width=300, height=250)
      thumb = img.execute_transforms(output_encoding=images.PNG)
      new_image.large = db.Blob(uploaded_file.read())
      new_image.medium = db.Blob(thumb)
      new_image.save()
    return HttpResponse("ok", mimetype="text/plain")

def upload_project(request):
  if request.method == 'POST':
    from django.utils import simplejson
    validation = [request.POST['name']=='',request.POST['description']=='',request.POST['criteria']=='',request.POST['more_criteria']=='',(int(request.POST['picture_num'])<2)]
    logging.info('made it to here!')
    if True in validation:
      response = {'project':'',
                  'validation':validation}
      logging.info('name or criteria error')
      return HttpResponse(simplejson.dumps(response), content_type='application/json')
    logging.warning("trying to upload project")
    logging.warning(request.POST)
##    logging.warning(request.user)
    name = request.POST['name']
    new_project = Project(
      name = name,
      description = request.POST['description'],
      creator = request.user.client,
      reward = 0,
      criteria = request.POST['criteria'],
      more_criteria = request.POST['more_criteria'],
      slug = slugify(name)
      )
    logging.warning(name)
    new_project.save()
    project = Project.objects.get(name=name)
    return HttpResponse(simplejson.dumps({'project':name, 'validation':validation}), content_type="application/json")

def upload_files(request):
  if request.method == 'POST':
    return upload_project(request)
  else:
      project_form = create_project()
  context = {
    'project_form': project_form,
    'user': request.user,
    'session_key': request.session.session_key
    }
  return render_to_response('upload.html', context, context_instance = RequestContext(request))

class SignInForm(forms.Form):
  email = forms.CharField(max_length=100)
  password = forms.CharField(widget=forms.PasswordInput)
def signin(request): 
  if request.method == 'POST':
##    print "in signin post"
    form = SignInForm(request.POST)
    if form.is_valid():
      email = form.cleaned_data['email']
      password = form.cleaned_data['password']
      user = auth.authenticate(username=email, password=password)
      if user is not None:
        auth.login(request, user)
        return HttpResponseRedirect('/loggedin/')
      else:
        return HttpResponseRedirect('/signin/')
  else:
##    print "in signin else"
    form = SignInForm() 
##  print "in signin "
  return render_to_response('signin.html', {'form': form, 'user': request.user,},context_instance=RequestContext(request))

def loggedin(request):
  username = request.user.client.name
  return render_to_response('loggedin.html',{'username':username, 'user': request.user,})

def logout(request):
  auth.logout(request)
  return HttpResponseRedirect('/')
