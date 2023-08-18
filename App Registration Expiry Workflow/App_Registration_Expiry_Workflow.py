#!/usr/bin/env python
# coding: utf-8

# In[30]:


import msal
import requests
import json
import csv
from datetime import datetime, timedelta


# In[31]:


# Enter the details of your AAD app registration
client_id = ''
client_secret = ''
directory_id = ''
authority = 'https://login.microsoftonline.com/' + directory_id
scope = ['https://graph.microsoft.com/.default']


# In[32]:


# Create an MSAL instance providing the client_id, authority and client_credential parameters
client = msal.ConfidentialClientApplication(client_id, authority=authority, client_credential=client_secret)

# First, try to lookup an access token in cache
token_result = client.acquire_token_silent(scope, account=None)


# In[33]:


# If the token is available in cache, save it to a variable
if token_result:
  access_token = 'Bearer ' + token_result
  print('Access token was loaded from cache')

# If the token is not available in cache, acquire a new one from Azure AD and save it to a variable
if not token_result:
  token_result = client.acquire_token_for_client(scopes=scope)
  access_token = 'Bearer ' + token_result['access_token']
  print('New access token was acquired from Azure AD')


# In[34]:


def parse_ms_graph_date(date_str):
    # Remove the trailing 'Z' and fractional seconds, then parse the date
    date_str_without_z = date_str[:-1].split('.')[0]
    date_format = '%Y-%m-%dT%H:%M:%S'
    return datetime.strptime(date_str_without_z, date_format)


# In[35]:


EXPIRY_DAYS = 14
LOGIC_APP_HTTP_URL = ''

# Calculate the date range for the 14th day
exact_expiry_date = datetime.now() + timedelta(days=EXPIRY_DAYS)
start_of_day = exact_expiry_date.replace(hour=0, minute=0, second=0, microsecond=0)
end_of_day = exact_expiry_date.replace(hour=23, minute=59, second=59, microsecond=999999)


# In[36]:


# Get app registrations with expiring secrets
url = f'https://graph.microsoft.com/v1.0/applications'
headers = {
    'Authorization': f'{access_token}',
    'Accept': 'application/json'
}

response = requests.get(url, headers=headers)
response_data = json.loads(response.text)

expiring_apps = [
    app for app in response_data['value']
    if 'passwordCredentials' in app and any(
        start_of_day <= parse_ms_graph_date(cred['endDateTime']) <= end_of_day
        for cred in app['passwordCredentials']
    )
]


# In[37]:


# Process expiring apps
for app in expiring_apps:
    owner_display_name = 'N/A'
    owner_email = None
    headers = {
    'Authorization': f'{access_token}',
    'Accept': 'application/json'
        }

    owner_url = f'https://graph.microsoft.com/v1.0/applications/{app["id"]}/owners'
    owner_response = requests.get(owner_url, headers=headers)
    owner_data = json.loads(owner_response.text)

    if 'value' in owner_data and len(owner_data['value']) > 0:
        owner = owner_data['value'][0]
        owner_display_name = owner.get('displayName', 'N/A')
        owner_email = owner.get('userPrincipalName', None)  # Retrieve owner's email

    secret_expiry = parse_ms_graph_date(app['passwordCredentials'][0]['endDateTime']).strftime('%Y-%m-%d %H:%M:%S')

    payload = {
        'appName': app['displayName'],
        'appId': app['id'],
        'owner': owner_display_name,
        'owner_mail': owner_email,  # Include owner's email
        'secretExpiry': secret_expiry
    }
    
    headers = {
    'Accept': 'application/json'
        }

    payload_response = requests.post(LOGIC_APP_HTTP_URL, json=payload, headers=headers)

    if payload_response.status_code == 202:
        print(f"Payload sent successfully for app '{app['displayName']}'")
    else:
        print(f"Failed to send payload for app '{app['displayName']}'")




