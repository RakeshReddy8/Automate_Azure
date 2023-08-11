#!/usr/bin/env python
# coding: utf-8

import msal
import json
import requests
import csv
import secrets
import string


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


#token_result = ""


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


def generate_password(length=10, chars=string.ascii_letters + string.digits + string.punctuation):
    password = ''.join(secrets.choice(chars) for i in range(length))
    if (any(char.isdigit() for char in password) and
        any(char.islower() for char in password) and
        any(char.isupper() for char in password) and
        any(char in string.punctuation for char in password)):
        return password
    else:
        return generate_password(length, chars)

# Get email addresses from CSV file
email_addresses = []
with open('emails.csv', 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        email_addresses.append(row[0])

# Make GET request to get user details
for email in email_addresses:
    url = f'https://graph.microsoft.com/beta/users(\'{email}\')'
    headers = {'Authorization': access_token, 'Content-type': 'application/json'}
    response = requests.get(url=url, headers=headers)
    graph_result = response.json()
    if response.status_code == 200:
        # Generate a random password
        password = generate_password()
        # Make POST request to create new user
        post_url = 'https://graph.microsoft.com/v1.0/users'
        post_data = {
            "accountEnabled": True,
            "displayName": graph_result['displayName'] + ' -' + ' Admin',
            "mailNickname": 'admin' + graph_result['mailNickname'],
            "userPrincipalName": 'admin' + graph_result['mailNickname'] + '@xk4mc.onmicrosoft.com',
            "passwordProfile" : {
                "forceChangePasswordNextSignIn": True,
                "password": password
            }
        }
        response = requests.post(url=post_url, headers=headers, json=post_data)
        if response.status_code == 201:
            # Send email to newly provisioned email address
            send_email_url = f'https://graph.microsoft.com/v1.0/users/{email}/sendMail'
            send_email_data = {
                "message": {
                    "subject": "Your new account credentials",
                    "body": {
                        "contentType": "Text",
                        "content": f"Username: {email}\nPassword: {password}"
                    },
                    "toRecipients": [
                        {
                            "emailAddress": {
                                "address": email
                            }
                        }
                    ]
                },
                "saveToSentItems": "false"
            }
            response = requests.post(url=send_email_url, headers=headers, json=send_email_data)
            if response.status_code == 202:
                print(f'Email sent successfully to email: {email}')
            else:
                print(f'Failed to send email to email: {email}')
        else:
            print(f'Failed to create user for email: {email}')
    else:
        print(f'Failed to get user details for email: {email}')


password


#Specify the MS Graph API endpoint you want to call, e.g. 'https://graph.microsoft.com/v1.0/groups' to get all groups in your organization
url = f'https://graph.microsoft.com/beta/users/{id}'
headers = {'Authorization': access_token, 'Content-type': 'application/json'}


# Initiate a variable to store data from all pages
graph_results = []
# Call the endpoint, if there is the @odata.nextLink property, set the url variable to it's value
# and continue making requests until looped through all pages
while url:
  try:
    graph_result = requests.get(url=url, headers=headers).json()
    graph_results.extend(graph_result['value'])
    url = graph_result['@odata.nextLink']
  except:
    break

#Specify the MS Graph API endpoint you want to call, e.g. 'https://graph.microsoft.com/v1.0/groups' to get all groups in your organization
url1 = 'https://graph.microsoft.com/v1.0/users'
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
            "accountEnabled": true,
            "displayName": f"{graph_result['displayName']} + Admin",
            "mailNickname": f"{graph_result['mailNickname']}",
            "userPrincipalName": "AdeleV@contoso.onmicrosoft.com",
            "passwordProfile" : {
                "forceChangePasswordNextSignIn": true,
                "password": "xWwvJ]6NMw+bWH-d"
                }
            }
        # Send POST request to reset redemption status
        response = requests.post(url=url, headers=headers, json=data)
        print(response.status_code)

