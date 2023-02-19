import json
import requests
import sys
import msal
from msal import PublicClientApplication

print("Script to invite user to Baker Hughes!")

client_id = '14d82eec-204b-4c2f-b7e8-296a70dab67e'
tenant_id = '5e58722e-83fd-4b8c-b0cf-0c6bd49959a1'

scopes = ['https://graph.microsoft.com/User.Read.All',
          'https://graph.microsoft.com/User.ReadWrite.All',
          'https://graph.microsoft.com/User.Invite.All',
          'https://graph.microsoft.com/CrossTenantInformation.ReadBasic.All',
          'https://graph.microsoft.com/Policy.Read.All']

# Check for too few or too many command-line arguments.
if (len(sys.argv) > 1) and (len(sys.argv) != 3):
  print("Usage: get-tokens.py <client ID> <tenant ID>")
  exit(1)

if len(sys.argv) > 1:
  client_id = sys.argv[1]
  tenant_id = sys.argv[2]

app = PublicClientApplication(
  client_id = client_id,
  authority = "https://login.microsoftonline.com/" + tenant_id
)

acquire_tokens_result = app.acquire_token_interactive(
  scopes = scopes
)

if 'error' in acquire_tokens_result:
  print("Error: " + acquire_tokens_result['error'])
  print("Description: " + acquire_tokens_result['error_description'])
else:
  print("Access token acquired from Azure AD")
  #print(acquire_tokens_result['access_token'])
  #print("\nRefresh token:\n")
  #print(acquire_tokens_result['refresh_token'])

access_token = 'Bearer ' + acquire_tokens_result['access_token']
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
