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

#token_result = "eyJ0eXAiOiJKV1QiLCJub25jZSI6Im9DZDZTLW42eFlZNVE0UHp2OXRqeTFEOVhZSlotRTk3bzdKRWxtQWZMckkiLCJhbGciOiJSUzI1NiIsIng1dCI6Ii1LSTNROW5OUjdiUm9meG1lWm9YcWJIWkdldyIsImtpZCI6Ii1LSTNROW5OUjdiUm9meG1lWm9YcWJIWkdldyJ9.eyJhdWQiOiJodHRwczovL2dyYXBoLm1pY3Jvc29mdC5jb20vIiwiaXNzIjoiaHR0cHM6Ly9zdHMud2luZG93cy5uZXQvZDU4NGE0YjctYjFmMi00NzE0LWE1NzgtZmQ0ZDQzYzE0NmE2LyIsImlhdCI6MTY3NjA0NTM4NSwibmJmIjoxNjc2MDQ1Mzg1LCJleHAiOjE2NzYxMzIwODUsImFjY3QiOjAsImFjciI6IjEiLCJhY3JzIjpbInVybjp1c2VyOnJlZ2lzdGVyc2VjdXJpdHlpbmZvIiwiYzEiLCJjMiJdLCJhaW8iOiJBVlFBcS84VEFBQUFNQ3F1ZmpwYWluVy9TOG43bFd1QkhJNVJqWEdlRWhvcVZJUHlKMXpSS2pOLy92UnlaNmllMjBwdjVETkcrREdJWWxvRVA5STlWWTFGYVIvN0FONHEwd1ZrQmtwNlZJUkIxc3lmZHI4UHRkVT0iLCJhbXIiOlsicHdkIiwibWZhIl0sImFwcF9kaXNwbGF5bmFtZSI6Ik1pY3Jvc29mdCBBenVyZSBQb3dlclNoZWxsIiwiYXBwaWQiOiIxOTUwYTI1OC0yMjdiLTRlMzEtYTljZi03MTc0OTU5NDVmYzIiLCJhcHBpZGFjciI6IjAiLCJmYW1pbHlfbmFtZSI6IlJlZGR5IiwiZ2l2ZW5fbmFtZSI6IktvdnZ1cmkgUmFrZXNoIiwiaWR0eXAiOiJ1c2VyIiwiaXBhZGRyIjoiMTM0LjIzOC45LjEyOCIsIm5hbWUiOiJSZWRkeSwgS292dnVyaSBSYWtlc2ggLSBBZG1pbiIsIm9pZCI6IjA3ZmU2ZTEyLTQ0MmMtNDkzMi1hOTA5LWYzZGIwZDdlNDJkOSIsInBsYXRmIjoiMyIsInB1aWQiOiIxMDAzMjAwMjNGN0EyNkI5IiwicmgiOiIwLkFSSUF0NlNFMWZLeEZFZWxlUDFOUThGR3BnTUFBQUFBQUFBQXdBQUFBQUFBQUFBU0FBQS4iLCJzY3AiOiJBdWRpdExvZy5SZWFkLkFsbCBEaXJlY3RvcnkuQWNjZXNzQXNVc2VyLkFsbCBlbWFpbCBvcGVuaWQgcHJvZmlsZSIsInNpZ25pbl9zdGF0ZSI6WyJpbmtub3dubnR3ayJdLCJzdWIiOiItc2hQTkRjbHU1aEhqLTZGVmFIV0tVeHdQXzk5M1daRWJUVG9nMHVHUDRBIiwidGVuYW50X3JlZ2lvbl9zY29wZSI6Ik5BIiwidGlkIjoiZDU4NGE0YjctYjFmMi00NzE0LWE1NzgtZmQ0ZDQzYzE0NmE2IiwidW5pcXVlX25hbWUiOiJhZG1pbnJlZGRrb3ZAYmFrZXJodWdoZXMub25taWNyb3NvZnQuY29tIiwidXBuIjoiYWRtaW5yZWRka292QGJha2VyaHVnaGVzLm9ubWljcm9zb2Z0LmNvbSIsInV0aSI6IjJFNVZzcmlEbUVLM2MyWl93NlI5QVEiLCJ2ZXIiOiIxLjAiLCJ3aWRzIjpbIjliODk1ZDkyLTJjZDMtNDRjNy05ZDAyLWE2YWMyZDVlYTVjMyIsImZlOTMwYmU3LTVlNjItNDdkYi05MWFmLTk4YzNhNDlhMzhiMSIsImU4NjExYWI4LWMxODktNDZlOC05NGUxLTYwMjEzYWIxZjgxNCIsImYyZWY5OTJjLTNhZmItNDZiOS1iN2NmLWExMjZlZTc0YzQ1MSIsImI3OWZiZjRkLTNlZjktNDY4OS04MTQzLTc2YjE5NGU4NTUwOSJdLCJ4bXNfY2MiOlsiQ1AxIl0sInhtc19zc20iOiIxIiwieG1zX3N0Ijp7InN1YiI6IlpReG8tRTdITGRDS3RIRmR2XzN0Ykoydk5RTy1OR3BmZmhMZzZwUlZGYlEifSwieG1zX3RjZHQiOjE0MDI5OTIzMzN9.GxaDdeJ7DAYfIBIqaBwSSrCV3pSemH8LdNAs1RMlSgrQReJvHgYfJ0Ps4DuIJ2TSckwg15RQNU2mCguPg4HL2nceDVIZy8wAKtIMkHUbU8CUyvWysoO4_oQE0glmkhKgIVvB1PReArBNhkay5AxDpdmaFuLIkIIf3xkpFPzs2zTbC04MWrV4F-e1NODyKWzbdX8NhD-oTwi_z7hbOJaowi4rZTW2tQiI2iIdJEskNBUuEER-jtFB4TVuSYtu70J0p264FBL6WcCbIBWIbC974P6xphAYpX_VtpYhUgOnzU88gmwBgbGp8RVwh6o-MrJMByij46utSARn2CzwDxdZXQ"


# If the token is available in cache, save it to a variable
if token_result:
  access_token = 'Bearer ' + token_result
  print('Access token was loaded from cache')

# If the token is not available in cache, acquire a new one from Azure AD and save it to a variable
if not token_result:
  token_result = client.acquire_token_for_client(scopes=scope)
  access_token = 'Bearer ' + token_result['access_token']
  print('New access token was acquired from Azure AD')


headers = {'Authorization': access_token, 'Content-type': 'application/json'}

# Read CSV file
with open('delete_users.csv', 'r') as file:
    fieldnames = ['UPN']
    reader = csv.DictReader(file, fieldnames=fieldnames)
    next(reader) # skip header
    for row in reader:
        upn = row['UPN']
        # Use the email and object_id here
        print(upn)
        url = f'https://graph.microsoft.com/v1.0/users/{upn}'
        # Send POST request to reset redemption status
        response = requests.delete(url=url, headers=headers)
        print(response.status_code)

