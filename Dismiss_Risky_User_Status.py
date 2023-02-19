#!/usr/bin/env python
# coding: utf-8

import msal
import json
import requests
import csv

# Enter the details of your AAD app registration
client_id = 'e7bf7836-241a-4750-9682-5306e849d8a4'
client_secret = ''
directory_id = '5e58722e-83fd-4b8c-b0cf-0c6bd49959a1'
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


while True:
    # Get the guest email address from the user
    guest_email = input("Enter the user's email address or type 'exit' to quit: ")
    
    if guest_email == "exit":
        break
    else:
        user_detail = f"https://graph.microsoft.com/v1.0/users?$count=true&$filter=mail eq '{guest_email}'"
        resp = requests.get(url=user_detail, headers=headers)
        details = resp.json()
        objectId = details["value"][0]["id"]
        
        risky_url = f"https://graph.microsoft.com/beta/riskyUsers/{objectId}"
        risk_resp = requests.get(url=risky_url, headers=headers)
        risk_response = risk_resp.json()
        
        if risk_resp.status_code == 200:
            json_formatted_str = json.dumps(risk_response, indent=2)
            print(json_formatted_str)
            
            confirm = input(f"Would you like to dismiss {guest_email} risk status (y/n):")
            if confirm.lower() == "y":
                dismiss_url = 'https://graph.microsoft.com/v1.0/invitations'
                data = {
                    "userIds": f"{objectId}"
                    }
                        
                # Send POST request to reset redemption status
                response = requests.post(url=dismiss_url, headers=headers, json=data)
                if response.status_code == 204:
                    print(f"'{guest_email}' uset risk has been dimissed")
                else:
                    print("Error in dismissing user risk")
                    
            else:
                print('Dismiss process aborted')
        else:
            print(f"{guest_email} is not a Risky User")
