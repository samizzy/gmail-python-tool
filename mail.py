from __future__ import print_function

import os
import pickle
import base64
import sys
import getopt
import yaml

from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from apiclient import errors, discovery  #needed for gmail service

SCOPES = ['https://www.googleapis.com/auth/gmail.send']
SUBJECT = 'SUBJECT'
BODY = 'BODY'
SEP = '\t'
COMMENT_CHAR="#"

def get_contacts(filename):
    """
    Return two lists names, emails containing names and email addresses
    read from a file specified by filename.
    """
    names = []
    emails = []
    with open(filename, mode='r', encoding='utf-8') as contacts_file:
        for a_contact in contacts_file:
            arr = a_contact.split(SEP)
            if(not arr[0].startswith(COMMENT_CHAR)):
                names.append(arr[0])
                emails.append(arr[1].strip())
    return names, emails

def get_content_map(filename):
    """
    Returns a Dict containing SUBJECT and BODY as keys.
    """
    content_map = dict()
    with open(filename, 'r', encoding='utf-8') as template_file:
        current_tag = ''
        for line in template_file:
            if line.rstrip().endswith('START:'):
                current_tag=line.rstrip().split(':')[0]
                content_map[current_tag]= ''
            elif line.rstrip().endswith('END:'):
                current_tag=''
            elif current_tag != '':
                content_map[current_tag] = content_map[current_tag] + line

    return content_map 
    
def get_gmail_service():
    print('Conecting to google servers...')
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    return service

def send_message_without_attachment(service, user_id, message):
    message_as_bytes = message.as_bytes() # the message should converted from string to bytes.
    message_as_base64 = base64.urlsafe_b64encode(message_as_bytes) #encode in base64 (printable letters coding)
    json =  {'raw': message_as_base64.decode()}    # need to JSON serializable (no idea what does it means)

    try:
        message_sent = (service.users().messages().send(userId=user_id, body=json).execute())
        # message_id = message_sent['id']
        # print(attached_file)
        # print (f'Message sent (without attachment) \n\n Message Id: {message_id}\n\n Message:\n\n {json}')
        # return body
    except errors.HttpError as error:
        print (f'An error occurred: {error}')

def get_yml_as_dict(file_path):
    yml_dict = None
    with open(file_path, mode='r', encoding='utf-8') as f:
        yml_dict = yaml.load(f)
    return yml_dict

def main(args):
    user_email = ""
    template_file = ""
    contacts_file = ""
    yaml_file = ""

    help_string = "mail.py -t <template_file> -c <contacts> -p <common_yaml>"
    try:
        opts, args = getopt.getopt(args,"hu:t:c:p:",["user=","template=","contacts=","properties="])
    except getopt.GetoptError:
        print("Problem in parsing input!")
        print(f"Usage: {help_string}")
        sys.exit(2)
    
    for k,v in opts:
        if k == "-h" or k== "--help":
            print(f"Usage: {help_string}")
            sys.exit(0)
        elif k == "-u" or k == "--user":
            user_email = v
        elif k == "-t" or k == "--template":
            template_file = v
        elif k == "-c" or k == "--contacts":
            contacts_file = v
        elif k == "-p" or k == "--properties":
            yaml_file = v
    
    if(user_email == "" or template_file == "" or contacts_file == "" or yaml_file == ""):
        print(f"Usage: {help_string}")
        sys.exit(2)

    yml_dict = get_yml_as_dict(yaml_file)
    names, emails = get_contacts(contacts_file)
    content_map = get_content_map(template_file)

    subject_template = Template(content_map[SUBJECT])
    message_template = Template(content_map[BODY])
    service = get_gmail_service()

    # print(names)
    # print(f'All name list {names}')
    print(f'All email list {emails}')
    
    print('Sending email..')
    # For each contact, send the email:
    for name, email in zip(names, emails):
       
        message = message_template.substitute(yml_dict, PERSON_NAME = name.title())
        subject = subject_template.substitute(yml_dict)
        # print(subject)
        # print(message)

        # setup the parameters of the message
        msg = MIMEMultipart()  
        msg['From'] = user_email
        msg['To'] = email
        msg['Subject'] = subject
        
        # add in the message body
        msg.attach(MIMEText(message, 'html'))
        send_message_without_attachment(service, 'me', msg)
        print(f'sending to {email} done')
        del msg
        
    
if __name__ == '__main__':
    main(sys.argv[1:])