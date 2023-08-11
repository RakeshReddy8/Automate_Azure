#Set the below parameeters as per the Application Registration
$ApplicationID    = ""
$DirectoryID      = ""
$ClientSecret     = ""

$Body = @{    
Grant_Type    = "client_credentials"
Scope         = "https://graph.microsoft.com/.default"
client_Id     = $ApplicationID
Client_Secret = $ClientSecret
} 

$ConnectGraph = Invoke-RestMethod -Uri "https://login.microsoftonline.com/$DirectoryID/oauth2/v2.0/token" -Method POST -Body $Body

$AccessToken = $ConnectGraph.access_token

#Form request headers with the acquired $AccessToken
$headers = @{'Content-Type'="application\json";'Authorization'="Bearer $AccessToken"}
 
#This request get users list with signInActivity.
$ApiUrl = "https://graph.microsoft.com/v1.0/identityGovernance/entitlementManagement/connectedOrganizations/"
 

$main = (Import-Csv 'C:\Users\reddkov\xwing.csv') | ?{$_ -ne ''}


ForEach($mai in $main){
	$displayx = $mai.displayName
	$descriptionx = $mai.description
	$domainNamex = $mai.domainName
	$intgroupid = $mai.Internal_Sponsor_Group_Id
	$extgroupid = $mai.External_Sponsor_Group_Id

	$Body1 = @"
	{
		"displayName" : "$displayx",
		"description" : "$descriptionx",
		"identitySources" : [
		{
		"@odata.type" : "#microsoft.graph.domainIdentitySource",
		"domainName" :  "$domainNamex",
		"displayName" : "example.com"
		}
		],
		"state" : "proposed"
		}
		
"@
$Body1
	$Response = Invoke-RestMethod -Method POST -Uri $ApiUrl -Headers $headers -Body $Body1 -ContentType 'application/json'
	
	$Response
	$ID = $Response.id
	
#######################################

	$ApiUrl2 = "https://graph.microsoft.com/v1.0/identityGovernance/entitlementManagement/connectedOrganizations/$ID/internalSponsors/`$ref"
	$Body2 = @"
	{
		"@odata.id": "https://graph.microsoft.com/v1.0/groups/$intgroupid"
		}
"@
$Body2
$ApiUrl2
	$Response = Invoke-RestMethod -Method POST -Uri $ApiUrl2 -Headers $headers -Body $Body2 -ContentType 'application/json'
	
#########################################

	$ApiUrl3 = "https://graph.microsoft.com/v1.0/identityGovernance/entitlementManagement/connectedOrganizations/$ID/externalSponsors/`$ref"
	$Body3 = @"
	{
		"@odata.id": "https://graph.microsoft.com/v1.0/groups/$extgroupid"
		}
"@
$Body3
	$Response = Invoke-RestMethod -Method POST -Uri $ApiUrl3 -Headers $headers -Body $Body3 -ContentType 'application/json'
}
	




	




 
