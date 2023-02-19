#!/usr/bin/env python
# coding: utf-8

import msal
import json
import requests
import csv
import datetime
import copy

# Get current date and time
now = datetime.datetime.now()

# Find the date of the previous Monday
monday = now - datetime.timedelta(days=7)

# Format the date and time as a string in the format required by the URL
date_time = monday.strftime("%Y-%m-%dT11:30:00Z")
only_date = monday.strftime("%Y-%m-%d")
current_date = now.strftime("%Y-%m-%d")
current_date_time = now.strftime("%Y-%m-%dT11:30:00Z")

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
url = f"https://graph.microsoft.com/beta/auditLogs/signIns?$filter=userType eq 'guest' and conditionalAccessStatus eq 'Success' and crossTenantAccessType eq 'b2bCollaboration' and isInteractive eq true and authenticationRequirement eq 'multiFactorAuthentication' and (createdDateTime ge {date_time} and createdDateTime le {current_date_time})&$top=999"
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


# Create a copy of the item JSON data
json_data_copy = copy.deepcopy(graph_result['value'])

# Modify the copied data
for row in json_data_copy:
    row['incomingTokenType'] = row['incomingTokenType'].replace("none", "None").replace("primaryRefreshToken", "Primary refresh token").replace("Primary refresh token,saml11", "").replace("saml11", "SAML 1.1")
    if row['status']['errorCode'] == 0:
        row['status']['errorCode'] = ""

# open CSV file for writing
with open(f'SignIns_{only_date}_{current_date}.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
    fieldnames = ['Date (UTC)', 'Request ID', 'Correlation ID', 'User ID', 'User', 'Username', 'User type', 'Cross tenant access type', 'Incoming token type', 'Authentication Protocol', 'Unique token identifier', 'Client credential type', 'Application', 'Application ID ', 'Resource', 'Resource ID ', 'Resource tenant ID', 'Home tenant ID', 'Home tenant name', 'IP address', 'Location', 'Status', 'Sign-in error code', 'Failure reason', 'Client app', 'Device ID', 'Browser', 'Operating System', 'Compliant', 'Managed','Join Type', 'Multifactor authentication result', 'Multifactor authentication auth method', 'Multifactor authentication auth detail', 'Authentication requirement', 'Sign-in identifier', 'IP address (seen by resource)', 'Autonomous system  number', 'Flagged for review', 'Token issuer type', 'Incoming token type', 'Token issuer name', 'Latency', 'Conditional Access']
    
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    # write data to CSV
    for item in graph_result['value']:
        if item['uniqueTokenIdentifier'][0] in ["-","+"]:
            item['uniqueTokenIdentifier'] = "'" + item['uniqueTokenIdentifier']
            
        if item['status']['errorCode'] == 0:
            status = 'Success'
        else:
            status = 'Interrupted'
        location = item['location']['city']+', '+item['location']['state']+', '+item['location']['countryOrRegion']
        writer.writerow({
            'Date (UTC)': item['createdDateTime'],
            'Request ID': item['id'],
            'Correlation ID': item['correlationId'],
            'User ID': item['userId'],
            'User': item['userDisplayName'],
            'Username': item['userPrincipalName'],
            'User type': item['userType'],
            'Cross tenant access type': item['crossTenantAccessType'],
            'Incoming token type': item['incomingTokenType'],
            'Authentication Protocol': item['authenticationProtocol'],
            'Unique token identifier': item['uniqueTokenIdentifier'],
            'Client credential type': item['clientCredentialType'],
            'Application': item['appDisplayName'],
            'Application ID ': item['appId'],
            'Resource': item['resourceDisplayName'],
            'Resource ID ': item['resourceId'],
            'Resource tenant ID': item['resourceTenantId'],
            'Home tenant ID': item['homeTenantId'],
            'Home tenant name': item['homeTenantName'],
            'IP address': item['ipAddress'],
            'Location': location,
            'Status' : status,
            'Sign-in error code': item['status']['errorCode'],
            'Failure reason': item['status']['failureReason'],
            'Client app': item['clientAppUsed'],
            'Device ID': item['deviceDetail']['deviceId'],
            'Browser': item['deviceDetail']['browser'],
            'Operating System': item['deviceDetail']['operatingSystem'],
            'Compliant': item['deviceDetail']['isCompliant'],
            'Managed': item['deviceDetail']['isManaged'],
            'Join Type': item['deviceDetail']['trustType'],
            'Multifactor authentication result': item['status']['additionalDetails'],
            'Multifactor authentication auth method': item['mfaDetail']['authMethod'],
            'Multifactor authentication auth detail': item['mfaDetail']['authDetail'],
            'Authentication requirement': item['authenticationRequirement'].replace("multiFactorAuthentication", "Multifactor authentication"),
            'Sign-in identifier': item['signInIdentifier'],
            'IP address (seen by resource)': item['ipAddressFromResourceProvider'],
            'Autonomous system  number': item['autonomousSystemNumber'],
            'Flagged for review': item['flaggedForReview'],
            'Token issuer type': item['tokenIssuerType'].replace("AzureAD", "Azure AD"),
            'Incoming token type': item['incomingTokenType'],
            'Token issuer name': item['tokenIssuerName'],
            'Latency': item['processingTimeInMilliseconds'],
            'Conditional Access': item['conditionalAccessStatus'].replace("success", "Success")
            })
        
# Read the CSV file into a list of lists
with open(f'SignIns_{only_date}_{current_date}.csv', 'r', encoding='utf-8-sig') as file:
    reader = csv.reader(file)
    data = [row for row in reader]

# Update the values of the specific column (column 2) with values from the new JSON object
for i, row in enumerate(data[1:]):
    row[40] = json_data_copy[i]['incomingTokenType']
    row[22] = json_data_copy[i]['status']['errorCode']

# Write the modified data back to the CSV file
with open(f'SignIns_{only_date}_{current_date}.csv', 'w', newline='', encoding="utf-8-sig") as file:
    writer = csv.writer(file)
    writer.writerows(data)
