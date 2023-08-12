# Automate_Azure
The repository contains scripts in Python and PowerShell that use MS Graph API and Az PowerShell Modules to automate management tasks in Azure AD and Azure Cloud.

To run the scripts programmatically it is advised to create an App Registration in Azure AD with either Application or Delegated API Permissions.

Follow these steps to create the app registration:

1. Sign in to the Azure portal.
2. Click on Azure Active DIrectory and then select App regitrations from the main blade.
4. In the App Regitrations page, click on the 'New regitration' to create a new service principal.
5. After assigning relavant name, click on register.
6. In the newly created App regitration, click on 'API permissions', and select 'Add a permission' to assign relvant API permissions.
7. Finally create a secret for the App registration, through the 'Certificates & secrets' option. 
8. Before running the script insert the vaules for the below variables from the app regitration you've created.

client_id = '<>'  
client_secret = '<>'  
directory_id = '<>'  

For delgated permissions you can use username/password crednetials or you can genarate a access token from either Python/PowerShell script included in the repository [Generate Delegated Token](https://github.com/RakeshReddy8/Automate_Azure/tree/main/Generate%20Delgated%20Token).  
