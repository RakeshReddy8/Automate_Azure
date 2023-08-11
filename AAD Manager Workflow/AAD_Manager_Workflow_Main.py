#!/usr/bin/env python
# coding: utf-8

import msal
import json
import requests
import csv
import pandas as pd

from azure.identity import ManagedIdentityCredential
from azure.keyvault.secrets import SecretClient

credential = ManagedIdentityCredential()
client = SecretClient(vault_url="", credential=credential)

secret = client.get_secret("")

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


# If the token is available in cache, save it to a variable
if token_result:
  access_token = 'Bearer ' + token_result
  print('Access token was loaded from cache')

# If the token is not available in cache, acquire a new one from Azure AD and save it to a variable
if not token_result:
  token_result = client.acquire_token_for_client(scopes=scope)
  access_token = 'Bearer ' + token_result['access_token']
  print('New access token was acquired from Azure AD')

# Set up the Graph API endpoint and headers
graph_endpoint = "https://graph.microsoft.com/beta/users?$filter=onPremisesSyncEnabled ne true and userType eq 'Member' and accountEnabled eq true and startswith(userPrincipalName, 'admin')&$select=displayName,id,userPrincipalName&$count=true&$top=999"
manager_endpoint = "https://graph.microsoft.com/v1.0/users/{}/manager"
base_url = 'https://graph.microsoft.com/v1.0/'
users_endpoint = 'users'
headers = {
    "Authorization": access_token,
    "Content-Type": "application/json",
    'ConsistencyLevel': 'eventual'
}
payloadheaders = {"Content-Type": "application/json"}

# Set up the URL for sending JSON payload to relevant logic App HTTP connector if manager not found
send_payload_url = ""
remediate_payload_url = ""
remediate_fail_payload_url = ""

# Fetch users using the Graph API endpoint
response = requests.get(graph_endpoint, headers=headers)
users_data = response.json()

# Iterate over the users
for user in users_data['value']:
    user_id = user['id']
    user_upn = user['userPrincipalName']

    # Fetch manager details using the manager endpoint
    manager_url = manager_endpoint.format(user_id)
    response = requests.get(manager_url, headers=headers)
    manager_data = response.json()

    # Check if manager found
    if 'error' in manager_data:
        # Manager not found, search for the manager using existing users' details
        username = user_upn.split('@')[0]
        username = username[5:] if username.lower().startswith('admin') else username
        print(username)

        query = f"$filter=mailNickname eq '{username}'"
        existing_user_url = f"{base_url}{users_endpoint}?{query}"
        response = requests.get(existing_user_url, headers=headers)
        existing_user_data = response.json()
        print(existing_user_data)

        if 'value' in existing_user_data and len(existing_user_data['value']) > 0:
            missing_manager_upn = existing_user_data['value'][0]['userPrincipalName']
            
            
            # Update the user's manager using the Graph API
            user_url = f"{base_url}{users_endpoint}/{user_upn}/manager/$ref"
            payload = {
                "@odata.id": f"https://graph.microsoft.com/v1.0/users/{missing_manager_upn}"
            }
            response = requests.put(user_url, headers=headers, json=payload)
            
            # Check if the manager update was successful
            if response.status_code == 204:
                print(f"Successfully updated manager for user {user_upn}")
                user_details = {
                    'userPrincipalName': user_upn,
                    'displayName': user['displayName'],
                    'Manager Display Name': existing_user_data['value'][0]['displayName'],
                    'Manager Email': existing_user_data['value'][0]['mail']
                }
                payload = json.dumps(user_details)
                payloadheaders = {"Content-Type": "application/json"}
                response = requests.post(remediate_payload_url, headers=payloadheaders, data=payload)
                 
            else:
                print(f"Failed to update manager for user {user_upn}: {response.text}")
                user_details = {
                    'userPrincipalName': user_upn,
                    'displayName': user['displayName'],
                    'Manager Display Name': existing_user_data['value'][0]['displayName'],
                    'Manager Email': existing_user_data['value'][0]['mail']
                }
                print(user_details)
                payload = json.dumps(user_details)
                payloadheaders = {"Content-Type": "application/json"}
                response = requests.post(remediate_fail_payload_url, headers=payloadheaders, data=payload)
            
            print(f"Manager found using existing user details: {missing_manager_upn}")
            
        else:
            # Manager still not found, send JSON payload
            user_details = {
                'userPrincipalName': user_upn,
                'displayName': user['displayName']
            }

            disable_user_endpoint = f"https://graph.microsoft.com/v1.0/users/{user_upn}"
            disable_user_payload = {"accountEnabled": False}
            disable_user_payload_json = json.dumps(disable_user_payload)

            disable_user_endpoint_response = requests.patch(disable_user_endpoint, headers=headers, data=disable_user_payload_json)
            print(disable_user_endpoint_response) 

            if disable_user_endpoint_response.status_code == 204:
                payload = json.dumps(user_details)
                response = requests.post(send_payload_url, headers=payloadheaders, data=payload)
                print(f"No manager found for user {user_upn}. JSON payload sent. User Disabled")
            else:
                continue
    else:
        # Manager found using manager endpoint
        manager_upn = manager_data['userPrincipalName']
        print(f"Manager found for user {user_upn}: {manager_upn}")

