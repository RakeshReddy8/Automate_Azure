#!/usr/bin/env python
# coding: utf-8

import msal
import json
import requests
import csv

# Enter the details of your AAD app registration
client_id = ''
client_secret = ''
directory_id = ''
authority = 'https://login.microsoftonline.com/' + directory_id
scope = ['https://graph.microsoft.com/.default']

# Create an MSAL instance providing the client_id, authority and client_credential parameters
client = msal.ConfidentialClientApplication(client_id, authority=authority, client_credential=client_secret)

# First, try to lookup an access token in cache
token_result = client.acquire_token_silent(scope, account=None)

'''
#token_result = "<>" 
Connect-AzAccount
$value = Get-AzAccessToken -ResourceUrl "https://graph.microsoft.com/"
$value.Token
'''

# If the token is available in cache, save it to a variable
if token_result:
  access_token = 'Bearer ' + token_result
  print('Access token was loaded from cache')

# If the token is not available in cache, acquire a new one from Azure AD and save it to a variable
if not token_result:
  token_result = client.acquire_token_for_client(scopes=scope)
  access_token = 'Bearer ' + token_result['access_token']
  print('New access token was acquired from Azure AD')

print(access_token)

#Specify the MS Graph API endpoint you want to call, e.g. 'https://graph.microsoft.com/v1.0/groups' to get all groups in your organization
url = 'https://graph.microsoft.com/v1.0/invitations'
headers = {'Authorization': access_token, 'Content-type': 'application/json'}

# Read CSV file
with open('guest_users1.csv', 'r') as file:
    fieldnames = ['Email_ID','Object_ID']
    reader = csv.DictReader(file, fieldnames=fieldnames)
    next(reader) # skip header
    for row in reader:
        email = row['Email_ID']
        object_id = row['Object_ID']
        # Use the email and object_id here
        print(email, object_id)
        # Set request body
        data = { 
           "invitedUserEmailAddress": f"{email}",  
           "sendInvitationMessage": True,  
           "invitedUserMessageInfo": {  
              "messageLanguage": "en-US",  
              "customizedMessageBody": "Welcome to Baker Hughes!"  
        },  
        "inviteRedirectUrl": "https://myapps.microsoft.com",  
        "invitedUser": {  
           "id": f"{object_id}"  
        }, 
        "resetRedemption": True 
        }
        # Send POST request to reset redemption status
        response = requests.post(url=url, headers=headers, json=data)
        print(response.status_code)
