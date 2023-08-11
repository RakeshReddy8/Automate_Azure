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
    guest_email = input("Enter the guest user's email address or type 'exit' to quit: ")
    
    if guest_email == "exit":
        break
    else:
        # Check if the guest user already exists
        check_response = requests.get(url=f"https://graph.microsoft.com/v1.0/users?$count=true&$filter=mail eq '{guest_email}'&$select=externalUserState", headers=headers)
        check_data = check_response.json()

        if check_data['value']:
            # Guest user already exists
            if check_data['value'][0]['externalUserState'] == 'PendingAcceptance':
                confirm = input(f"Guest user with email '{guest_email}' already exists with 'Pending Acceptance' state. Do you want to resend invitation? (y,n)")
                if confirm.lower() == "y":
                    user_detail = f"https://graph.microsoft.com/v1.0/users?$count=true&$filter=mail eq '{guest_email}'"
                    # Make the API request
                    resp = requests.get(url=user_detail, headers=headers)
                    details = resp.json()
                    objectId = details["value"][0]["id"] 
                    
                    url = 'https://graph.microsoft.com/v1.0/invitations'
                    data = { 
                       "invitedUserEmailAddress": f"{guest_email}",  
                       "sendInvitationMessage": True,  
                       "invitedUserMessageInfo": {  
                          "messageLanguage": "en-US",  
                          "customizedMessageBody": "Welcome to Baker Hughes!"  
                    },  
                    "inviteRedirectUrl": "https://myapps.microsoft.com",  
                    "invitedUser": {  
                       "id": f"{objectId}"  
                    } 
                    }
                    # Send POST request to reset redemption status
                    response = requests.post(url=url, headers=headers, json=data)
                    if response.status_code == 201:
                        print(f"Invitation has been resent to Guest user '{guest_email}'")
                    else:
                        print("Error in sending invite to guest user")
            
            elif check_data['value'][0]['externalUserState'] is None:
                confirm = input(f"Guest user with email '{guest_email}' already exists with 'null' state. Do you want to invite internal guest user to B2B collaboration? (y/n)")
                if confirm.lower() == "y":
                    user_detail = f"https://graph.microsoft.com/v1.0/users?$count=true&$filter=mail eq '{guest_email}'"
                    # Make the API request
                    resp = requests.get(url=user_detail, headers=headers)
                    details = resp.json()
                    objectId = details["value"][0]["id"] 
                    
                    url = 'https://graph.microsoft.com/v1.0/invitations'
                    data = { 
                       "invitedUserEmailAddress": f"{guest_email}",  
                       "sendInvitationMessage": True,  
                       "invitedUserMessageInfo": {  
                          "messageLanguage": "en-US",  
                          "customizedMessageBody": "Welcome to Baker Hughes!"  
                    },  
                    "inviteRedirectUrl": "https://myapps.microsoft.com", 
                    }
                    # Send POST request to reset redemption status
                    response = requests.post(url=url, headers=headers, json=data)
                    if response.status_code == 201:
                        print(f"Guest user '{guest_email}' has been invited to B2B collaboration")
                    else:
                        print("Error in inviting guest user to B2B collaboration")
            
            elif check_data['value'][0]['externalUserState'] == 'Accepted':                   
                confirm = input(f"Guest user with email '{guest_email}' already exists with 'Accepted' state. Do you want to reset invitation status? (y/n)")
                if confirm.lower() == "y":
                    user_detail = f"https://graph.microsoft.com/v1.0/users?$count=true&$filter=mail eq '{guest_email}'"
                    # Make the API request
                    resp = requests.get(url=user_detail, headers=headers)
                    details = resp.json()
                    objectId = details["value"][0]["id"] 
                    
                    url = 'https://graph.microsoft.com/v1.0/invitations'
                    data = { 
                       "invitedUserEmailAddress": f"{guest_email}",  
                       "sendInvitationMessage": True,  
                       "invitedUserMessageInfo": {  
                          "messageLanguage": "en-US",  
                          "customizedMessageBody": "Welcome to Baker Hughes!"  
                    },  
                    "inviteRedirectUrl": "https://myapps.microsoft.com",  
                    "invitedUser": {  
                       "id": f"{objectId}"  
                    }, 
                    "resetRedemption": True 
                    }
                    # Send POST request to reset redemption status
                    response = requests.post(url=url, headers=headers, json=data)
                    if response.status_code == 201:
                        print(f"Guest user '{guest_email}' invitation status has been reset and a fresh invitation has been sent.")
                    else:
                        print("Error in resetting user invitation status")
        else:
            
            domain = guest_email.split('@')[1]
            org_detail = f"https://graph.microsoft.com/beta/tenantRelationships/findTenantInformationByDomainName(domainName='{domain}')"
            resp = requests.get(url=org_detail, headers=headers)
            details = resp.json()
            tenantId = details["tenantId"]
            
            trust_check = f"https://graph.microsoft.com/v1.0/policies/crossTenantAccessPolicy/partners/{tenantId}"
            response = requests.get(url=trust_check, headers=headers)
            if response.status_code == 200:
                print("User ID is from an Approved Domain")
                # Ask user if they want to invite the guest user
                confirm = input(f"Do you want to invite guest user with email '{guest_email}'? (y/n)")
                if confirm.lower() == "y":
                    # Invite the guest user
                    invite_data = {
                        "invitedUserEmailAddress": guest_email,
                        "sendInvitationMessage": True,
                        "inviteRedirectUrl": "https://myapplications.microsoft.com",
                        "invitedUserMessageInfo": {
                            "messageLanguage": "en-US",
                            "customizedMessageBody": "Welcome to Baker Hughes!"
                        }
                        }
                    invite_response = requests.post(url="https://graph.microsoft.com/v1.0/invitations", headers=headers, data=json.dumps(invite_data))

                    if invite_response.status_code == 201:
                            # Invitation sent successfully
                            print(f"Invitation sent to guest user with email '{guest_email}'.")
                    else:
                        # Error sending invitation
                            print("Error sending invitation. Please try again.")
                else:
                        print("Invitation not sent.")
            else:
                print("User ID is not from an Approved Domain")
