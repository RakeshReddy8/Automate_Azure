#!/usr/bin/env python
# coding: utf-8

import msal
import json
import requests
import csv
import pandas as pd

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


#token_result = "eyJ0eXAiOiJKV1QiLCJub25jZSI6ImJOWGRVVUZMVmZTVHhvOEJ5ejRxbkJ0anVZMHl3MXE0VzY4cFNna1QxZmsiLCJhbGciOiJSUzI1NiIsIng1dCI6Ii1LSTNROW5OUjdiUm9meG1lWm9YcWJIWkdldyIsImtpZCI6Ii1LSTNROW5OUjdiUm9meG1lWm9YcWJIWkdldyJ9.eyJhdWQiOiJodHRwczovL2dyYXBoLm1pY3Jvc29mdC5jb20iLCJpc3MiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC9kNTg0YTRiNy1iMWYyLTQ3MTQtYTU3OC1mZDRkNDNjMTQ2YTYvIiwiaWF0IjoxNjgzODE3MTgxLCJuYmYiOjE2ODM4MTcxODEsImV4cCI6MTY4MzgyMjQxNiwiYWNjdCI6MCwiYWNyIjoiMSIsImFjcnMiOlsidXJuOnVzZXI6cmVnaXN0ZXJzZWN1cml0eWluZm8iLCJjMSIsImMyIl0sImFpbyI6IkFWUUFxLzhUQUFBQWdFb3FMYTk4UmxRWVBadmdpakh2bmhzVGpCMXIvNzM1MU1pbERxMXQyTnJjNnhIR2RMQjI3RWZwOENEaEl4WFNUektvcVBGSlllZUJ4M1dUdTczbXVucEhBU3Y4QVZYcThoWDcyRVpUUkRFPSIsImFtciI6WyJwd2QiLCJtZmEiXSwiYXBwX2Rpc3BsYXluYW1lIjoiTWljcm9zb2Z0IEdyYXBoIENvbW1hbmQgTGluZSBUb29scyIsImFwcGlkIjoiMTRkODJlZWMtMjA0Yi00YzJmLWI3ZTgtMjk2YTcwZGFiNjdlIiwiYXBwaWRhY3IiOiIwIiwiZmFtaWx5X25hbWUiOiJSZWRkeSIsImdpdmVuX25hbWUiOiJLb3Z2dXJpIFJha2VzaCIsImlkdHlwIjoidXNlciIsImlwYWRkciI6IjEzNC4yMzguMTYuNjciLCJuYW1lIjoiUmVkZHksIEtvdnZ1cmkgUmFrZXNoIC0gQWRtaW4iLCJvaWQiOiIwN2ZlNmUxMi00NDJjLTQ5MzItYTkwOS1mM2RiMGQ3ZTQyZDkiLCJwbGF0ZiI6IjMiLCJwdWlkIjoiMTAwMzIwMDIzRjdBMjZCOSIsInJoIjoiMC5BUklBdDZTRTFmS3hGRWVsZVAxTlE4RkdwZ01BQUFBQUFBQUF3QUFBQUFBQUFBQVNBQUEuIiwic2NwIjoiQXBwUm9sZUFzc2lnbm1lbnQuUmVhZFdyaXRlLkFsbCBBdWRpdExvZy5SZWFkLkFsbCBDaGF0LkNyZWF0ZSBDaGF0LlJlYWQgQ2hhdC5SZWFkQmFzaWMgQ2hhdC5SZWFkV3JpdGUgQ2hhdE1lc3NhZ2UuUmVhZCBDaGF0TWVzc2FnZS5TZW5kIENsb3VkUEMuUmVhZC5BbGwgRGV2aWNlLlJlYWQuQWxsIERpcmVjdG9yeS5SZWFkLkFsbCBlbWFpbCBJZGVudGl0eVJpc2t5VXNlci5SZWFkLkFsbCBJZGVudGl0eVJpc2t5VXNlci5SZWFkV3JpdGUuQWxsIG9wZW5pZCBPcmdhbml6YXRpb24uUmVhZC5BbGwgT3JnYW5pemF0aW9uLlJlYWRXcml0ZS5BbGwgcHJvZmlsZSBVc2VyLlJlYWQgVXNlci5SZWFkLkFsbCBVc2VyLlJlYWRXcml0ZS5BbGwgVXNlckF1dGhlbnRpY2F0aW9uTWV0aG9kLlJlYWQuQWxsIiwic2lnbmluX3N0YXRlIjpbImlua25vd25udHdrIl0sInN1YiI6Ii1zaFBORGNsdTVoSGotNkZWYUhXS1V4d1BfOTkzV1pFYlRUb2cwdUdQNEEiLCJ0ZW5hbnRfcmVnaW9uX3Njb3BlIjoiTkEiLCJ0aWQiOiJkNTg0YTRiNy1iMWYyLTQ3MTQtYTU3OC1mZDRkNDNjMTQ2YTYiLCJ1bmlxdWVfbmFtZSI6ImFkbWlucmVkZGtvdkBiYWtlcmh1Z2hlcy5vbm1pY3Jvc29mdC5jb20iLCJ1cG4iOiJhZG1pbnJlZGRrb3ZAYmFrZXJodWdoZXMub25taWNyb3NvZnQuY29tIiwidXRpIjoieU1kYXM2OFFPMHlNT2lPS1M5T1hBQSIsInZlciI6IjEuMCIsIndpZHMiOlsiZmU5MzBiZTctNWU2Mi00N2RiLTkxYWYtOThjM2E0OWEzOGIxIiwiZjJlZjk5MmMtM2FmYi00NmI5LWI3Y2YtYTEyNmVlNzRjNDUxIiwiYjc5ZmJmNGQtM2VmOS00Njg5LTgxNDMtNzZiMTk0ZTg1NTA5Il0sInhtc19zdCI6eyJzdWIiOiJzREhHUVZGMGFpVVpiSjVaODdNQVhMVktCdlRMNWNvdVdVbXVSWnZ3NWF3In0sInhtc190Y2R0IjoxNDAyOTkyMzMzfQ.sIu_ZiwPJZM_Ni-KwuCifNkZ81syFUm5_eQsEDsVpn3UgSnKzISQkk_MrvK6T4S5Kbx0yidpb4K3HDBkJDLNuPGPYZtv-5zqKkC-yr9t2wYq6Diq6pRc4TPLye58sb-WDDP413VIYxS9wV3bAyGSLzhrXX5-pBkcxVPAxNi7PkQkfQORA0VWlHT8gVeCXdaT5IcvmdxHumM85AMY9xa1CorPkIbAa7QlWNwokzc-kXmSqxvaop4G3rGXfDTGCiDjmovBUaJhrxp0mCtx-eMu5b7KlhHSYp-Z1Ia8Esc-hONCoEwfvQJyYW1v4wS8tT5uTBXsChD-lDCMLPYdYZLgmw"


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
graph_endpoint = "https://graph.microsoft.com/beta/users?$filter=onPremisesSyncEnabled ne true and userType eq 'Member' and accountEnabled eq true and startswith(userPrincipalName, 'admin')&$select=displayName,id,userPrincipalName&$count=true"
headers = {'Authorization': access_token, 'Content-type': 'application/json', 'ConsistencyLevel': 'eventual'}


# Initiate a variable to store data from all pages
graph_results = []
# Call the endpoint, if there is the @odata.nextLink property, set the url variable to it's value
# and continue making requests until looped through all pages
while graph_endpoint:
  try:
    graph_result = requests.get(graph_endpoint, headers=headers).json()
    graph_results.extend(graph_result['value'])
    graph_endpoint = graph_result['@odata.nextLink']
  except:
    break


# Parse the JSON response
users = graph_results

# Specify the CSV file path
csv_file = 'user_details.csv'

# Open the CSV file in write mode
with open(csv_file, 'w', newline='') as file:
    # Create a CSV writer
    writer = csv.writer(file)

    # Write the header row
    writer.writerow(['DisplayName', 'userPrincipalName', 'Manager', 'Manager_Mail'])

    # Loop through the users
    for user in users:
        display_name = user['displayName']
        user_id = user['id']
        UPN = user['userPrincipalName']

        # Specify the MS Graph API endpoint to get the manager for each user
        manager_endpoint = f"https://graph.microsoft.com/v1.0/users/{user_id}/manager"

        # Make a GET request to the Microsoft Graph API to get the user's manager
        response = requests.get(manager_endpoint, headers=headers)

        # Check if the request was successful
        if response.status_code:
            # Parse the JSON response
            manager_data = response.json()
            manager = manager_data['displayName'] if 'displayName' in manager_data else None
            manager_mail = manager_data['mail'] if 'mail' in manager_data else None
            writer.writerow([display_name, UPN, manager, manager_mail])
        else:
            print(f"Error: {response.status_code} - {response.text}")

print(f"User details exported to {csv_file} successfully.")



