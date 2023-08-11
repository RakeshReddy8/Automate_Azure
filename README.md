# Automate_Azure
The repository contains scripts in Python and PowerShell that use MS Graph API and Az PowerShell Modules to automate management tasks in Azure AD and Azure Cloud.

To run the scripts programmatically it is advised to create an App Registration in Azure AD with either Application or Delegated API Permissions.

Once you create an App Regitration you will be provided with Application (Client) ID and you will be required to create the secret. You will need to assign required MS Graph API permission as necessary for the script to fucntion.


client_id = '<>'  
client_secret = '<>'  
directory_id = '<>'  
authority = 'https://login.microsoftonline.com/' + directory_id  
scope = ['https://graph.microsoft.com/.default']  
