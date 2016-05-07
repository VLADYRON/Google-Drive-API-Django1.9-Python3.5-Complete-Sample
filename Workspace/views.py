'''
Major references:
1. Django Google API Sample:
https://github.com/google/google-api-python-client/tree/master/samples/django_sample

2. http://engineering.hackerearth.com/2014/06/07/using-google-apis-in-django/

3. python-social-auth LIBRARY
http://stackoverflow.com/questions/29058520/how-to-sign-in-with-the-google-api-using-django

4. http://www.marinamele.com/use-the-google-analytics-api-with-django

5. Storage Class
https://developers.google.com/api-client-library/python/guide/django#storage

6. Google Python Video
https://www.youtube.com/watch?v=IVjZMIWhz3Y
'''

'''NECESSARY LIB FILES'''
import os
import logging
import httplib2

from googleapiclient.discovery import build
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseRedirect
from django.shortcuts import render
from Workspace.models import *
from test_google_drive_api_django import settings
from oauth2client.contrib import xsrfutil
from oauth2client.client import flow_from_clientsecrets
from oauth2client.contrib.django_orm import Storage

# CLIENT_SECRETS, name of a file containing the OAuth 2.0 information for this
# application, including client_id and client_secret, which are found
# on the API Access tab on the Google APIs
# Console <http://code.google.com/apis/console>
CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), '..', 'client_secrets.json')

FLOW = flow_from_clientsecrets(
    CLIENT_SECRETS,
    scope='https://www.googleapis.com/auth/drive',
    redirect_uri='http://127.0.0.1:8000/oauth2callback')



def index(request):

  '''I Have created a static user as I dont have any logged in user in my app right now'''
  U = User(
      username = 'example',
      firstname= 'Bla Bla',
      lastname= 'Bla Bla',
      email = 'example@gmail.com'
  )
  U.save()

  #This is a class created by google to save the credentials automatically in the database
  storage = Storage(CredentialsModel, 'id', U, 'credential')
  credential = storage.get()
  if credential is None or credential.invalid == True:
    FLOW.params['state'] = xsrfutil.generate_token(settings.SECRET_KEY,
                                                   U)
    authorize_url = FLOW.step1_get_authorize_url()
    print(authorize_url)
    return HttpResponseRedirect(authorize_url)
  else:
    http = httplib2.Http()
    http = credential.authorize(http)
    service = build('drive', 'v3', http=http)

    #GOOGLE DRIVE FUNCTION CALLS
    id = creatingNewFolder(service)
    id1 = creatingFolderInsideAFolder(service, id)
    print("Successful")
    return HttpResponse("Folder Id: "+id+" Subfolder Id: "+id1)


def auth_return(request):
  '''The Token generated in index() should be validated here with the same user that was used to generate the token'''
  U = User(
      username = 'example',
      firstname= 'Bla Bla',
      lastname= 'Bla Bla',
      email = 'example@gmail.com'
  )
  '''
  Reference:
  1. https://github.com/tschellenbach/Django-facebook/pull/564
  2. encode() is used here because in Django 1.6 or less we used to get the string automatically
  but in Django 1.7+ we have to use encode() to get the string
  '''
  if not xsrfutil.validate_token(settings.SECRET_KEY, (request.GET['state']).encode('utf-8'),
                                 U):
    print("Test: 1")
    return  HttpResponseBadRequest()
  print("Test: 2")
  credential = FLOW.step2_exchange(request.GET)
  storage = Storage(CredentialsModel, 'id', U, 'credential')
  storage.put(credential)
  return HttpResponseRedirect("/")



'''Functions For Drive'''



def creatingNewFolder(service):
    file_metadata = {
        'name': 'Test Folder Drive',
        'mimeType': 'application/vnd.google-apps.folder'
    }
    file = service.files().create(body=file_metadata,
                                  fields='id').execute()
    print('Folder ID: %s' % file.get('id'))
    return file.get('id')


def creatingFolderInsideAFolder(service, id):
    # folder_id = id
    file_metadata = {
        'name': 'Folder inside a folder Test',
        'parents': [id],
        'mimeType': 'application/vnd.google-apps.folder'
    }
    root_folder = service.files().create(body=file_metadata).execute()
    print('Folder Inside Folder ID: %s' % root_folder['id'])
    return root_folder['id']


# This function checks if any particular folder exists
# If it exists it just returns its id otherwise that folder is created and id is returned
def getFolderID(service):
    page_token = None
    while True:
        response = service.files().list(q="mimeType='application/vnd.google-apps.folder'",
                                              spaces='drive',
                                              fields='nextPageToken, files(id, name)',
                                              pageToken=page_token).execute()
        for file in response.get('files', []):
            # Process change
            #print('Found file: %s (%s)' % (file.get('name'), file.get('id')))
            if file.get('name')=='Test Folder Drive':
                return file.get('id')
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            id = creatingNewFolder(service)
            return id



