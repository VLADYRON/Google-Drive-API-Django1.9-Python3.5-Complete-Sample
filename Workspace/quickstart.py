from __future__ import print_function
import httplib2
import os

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

try:
    import argparse

    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Drive API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'drive-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:  # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def main():
    """Shows basic usage of the Google Drive API.

    Creates a Google Drive API service object and outputs the names and IDs
    for up to 10 files.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)

    '''results = service.files().list(
        pageSize=20,fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])
    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            print('{0} ({1})'.format(item['name'], item['id']))'''

    #id = creatingNewFolder(service)
    #id1 = creatingFolderInsideAFolder(service, id)
    #getFolderID(service)


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


if __name__ == '__main__':
    main()