# Automate_Azure
This repository contains scripts in Python and PowerShell that use MS Graph API and Az PowerShell Modules to automate management tasks in Azure AD and Azure Cloud.

To run the scripts programmatically it is advised to create an App Registration in Azure AD with either Application or Delegated API Permissions. Please note that if your admin has restricted the creation of App registrations to admins only, then you need to have any of the below Azure AD Roles to create the same.
- Application administrator
- Application developer
- Cloud application administrator

Follow these steps to create the app registration in Azure Active Directory:

1. Sign into Azure portal.
2. Click on Azure Active Directory and then select App regitrations from the main blade.
4. In the App Regitrations page, click on the 'New regitration' to create a new service principal.
5. After assigning relevant name, click on register.
6. In the newly created App regitration, click on 'API permissions', and select 'Add a permission' to assign relevant API permissions.
7. Finally create a secret for the App registration, through the 'Certificates & secrets' option. 
8. Before running the script insert the values for the below variables from the app regitration you've created.

client_id = '<>'  
client_secret = '<>'  
directory_id = '<>'  

For delegated permissions you can use username/password credentials or you can generate a access token from either Python/PowerShell script included in the repository [Generate Delegated Token](https://github.com/RakeshReddy8/Automate_Azure/tree/main/Generate%20Delgated%20Token).  
