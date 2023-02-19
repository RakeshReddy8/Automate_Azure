#!/usr/bin/env python

import msal
import json
import requests
import csv
import secrets
import string

print("Script to add users to 'O365licensing-PowerAppsGuests' security group")
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

def check_security_group_membership(email):
    # Define the API endpoint to check security group membership
    endpoint = f"https://graph.microsoft.com/v1.0/groups/4f2d5e7e-1b92-4066-8554-6addee9640ad/members?$count=true&$filter=mail/any(i:i eq '{email}')"

    # Add your Microsoft Graph API access token to the header
    headers = {
        "Authorization": access_token,
        "Content-Type": "application/json",
        "ConsistencyLevel": "eventual"
    }

    # Make the API request
    response = requests.get(url=endpoint, headers=headers)

    # Check the response status code
    if response.status_code == 200:
        # If the status code is 200, parse the response as JSON
        result = response.json()

        # Return the count of matching members
        return result["@odata.count"]
    else:
        # If the status code is not 200, return None
        return None

def add_user_to_security_group(email):
    
    # Add your Microsoft Graph API access token to the header
    headers = {
        "Authorization": access_token,
        "Content-Type": "application/json"
    }
    
    # Define the API endpoint to add get user object id
    user_detail = f"https://graph.microsoft.com/v1.0/users?$count=true&$filter=mail eq '{email}'"
    
    # Make the API request
    resp = requests.get(url=user_detail, headers=headers)
    details = resp.json()
    objectId = details["value"][0]["id"]   
    
    # Define the API endpoint to add a member to a security group
    endpoint = "https://graph.microsoft.com/v1.0/groups/4f2d5e7e-1b92-4066-8554-6addee9640ad/members/$ref"

    # Define the body of the API request
    body = {
        "@odata.id": f"https://graph.microsoft.com/v1.0/users/{objectId}"
    }

    # Make the API request
    response = requests.post(url=endpoint, headers=headers, data=json.dumps(body))

    # Check the response status code
    if response.status_code == 204:
        # If the status code is 204, the user was added to the security group
        return True
    else:
        # If the status code is not 204, the user was not added to the security group
        return False

    
while True:
    # Ask the user for their email address
    email = input("Enter the guest user's email address or 'exit' to quit: ")
    
    if email == "exit":
        break
    else:
        # Check if the user is a member of the security group
        membership_count = check_security_group_membership(email)
        
        if membership_count == 0:
            # If the user is not a member of the security group, ask the user if they want to add them
            add_user = input("The user is not a member of the 'O365licensing-PowerAppsGuests' security group. Would you like to add them? [y/n] ")
            
            if add_user.lower() == "y":
                # If the user wants to add the guest user to the security group, call the add_user_to_security_group function
                result = add_user_to_security_group(email)
                if result:
                    print(f"The user '{email}' is added to the security group.")
                else:
                    print("There was an error adding the user to the security group.")
        else:
            print(f"The user '{email}' is already part of the 'O365licensing-PowerAppsGuests' security group")

