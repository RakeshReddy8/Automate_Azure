#!/usr/bin/env python

import msal
import json
import requests
import csv
import openpyxl
import datetime


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


#Specify the MS Graph API endpoint you want to call, e.g. 'https://graph.microsoft.com/v1.0/groups' to get all groups in your organization
headers = {'Authorization': access_token, 'Content-type': 'application/json'}


now = datetime.datetime.utcnow()
current_date_time = now.strftime("%Y-%m-%dT%H:%M:%SZ")
current_date_time
while True:
    # Get the guest UPN address from the user
    guest_UPN = input("Enter the guest user's UPN address or type 'exit' to quit: ")
    
    if guest_UPN == "exit":
        break
    else:
        
        role_name = input("Enter the Azure AD role you want to assign: ")
        
        url = f"https://graph.microsoft.com/v1.0/roleManagement/directory/roleDefinitions?$filter=DisplayName eq '{role_name}'&$select=id"
        # Make the API call and retrieve the JSON response
        response = requests.get(url, headers=headers)
        response_json = json.loads(response.content)
        role_id = response_json['value'][0]['id']
        print(role_id)


        url = f"https://graph.microsoft.com/v1.0/users?$filter=userPrincipalName eq '{guest_UPN}'"
        # Make the API call and retrieve the JSON response
        response = requests.get(url, headers=headers)
        response_json = json.loads(response.content)
        object_id = response_json['value'][0]['id']
        print(object_id)


        url = 'https://graph.microsoft.com/v1.0/roleManagement/directory/roleEligibilityScheduleRequests'
        data = {
            "action": "adminAssign",
            "justification": "Assign Attribute Assignment Admin eligibility to restricted user",
            "roleDefinitionId": f"{role_id}",
            "directoryScopeId": "/",
            "principalId": f"{object_id}",
            "scheduleInfo": {
                "startDateTime": f"{current_date_time}",
                "expiration": {
                    "type": "noExpiration"
                    }
                }
            }

        # Send POST request to reset redemption status
        response = requests.post(url=url, headers=headers, json=data)
        if response.status_code == 201:
            print(f"User '{guest_UPN}' has been assigned {role_name} Azure AD role")
        else:
            print("Error in assiging Azure AD role")


