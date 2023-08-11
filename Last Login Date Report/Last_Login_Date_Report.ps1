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

#Invoke-WebRequest -Uri “https://download.microsoft.com/download/e/3/e/e3e9faf2-f28b-490a-9ada-c6089a1fc5b0/Product%20names%20and%20service%20plan%20identifiers%20for%20licensing.csv” -Outfile “identifier.csv”

$table = @{}
$file = Import-CSV -Path “identifier.csv” | ForEach-Object {$table[$_.GUID] = $_.'Product_Display_Name'}
 
#This request get users list with signInActivity.
$ApiUrl = "https://graph.microsoft.com/v1.0/users?`$filter=userType eq 'guest'&`$select=displayName,userPrincipalName,signInActivity,userType,assignedLicenses,accountEnabled,licenseAssignmentStates,externalUserState&`$top=999"
 
$Result = @()
While ($ApiUrl -ne $Null) #Perform pagination if next page link (odata.nextlink) returned.
{
$Response =  Invoke-RestMethod -Method GET -Uri $ApiUrl -Headers $headers
if($Response.value)
{
$Users = $Response.value
$Users
ForEach($User in $Users)
{
 
$Result += New-Object PSObject -property $([ordered]@{ 
DisplayName = $User.displayName
UserPrincipalName = $User.userPrincipalName
LastSignInDateTime = if($User.signInActivity.lastSignInDateTime) { [DateTime]$User.signInActivity.lastSignInDateTime } Else {$null}
LastNonInteractiveSignInDateTime = if($User.signInActivity.lastNonInteractiveSignInDateTime) { [DateTime]$User.signInActivity.lastNonInteractiveSignInDateTime } Else { $null }
IsLicensed  = if ($User.assignedLicenses.Count -ne 0) { $true } else { $false }
skuName = if($User.licenseAssignmentStates.assignedByGroup -ne $null){ ($w = ForEach($Use in $User.licenseAssignmentStates.skuId){$table[($Use)]}) -join ", "}
IsGuestUser  = if ($User.userType -eq 'Guest') { $true } else { $false }
ExternalUserState = $User.externalUserState
IsAccountEnabled = $User.accountEnabled
})
}
 
}
$ApiUrl=$Response.'@odata.nextlink'
}

#Un-Comment the below if you want the full sign-in logs report
$Result | Export-CSV "C:\temp\LastLoginDateReport.csv" -NoTypeInformation -Encoding UTF8

<#
$DaysInactive = 30
$dateTime = (Get-Date).Adddays(-($DaysInactive))
$Result | Where-Object { $_.LastSignInDateTime -eq $Null -OR $_.lastNonInteractiveSignInDateTime -eq $Null -OR ($_.LastSignInDateTime -le $dateTime -and $_.lastNonInteractiveSignInDateTime -le $dateTime)} | Export-CSV "C:\Users\reddkov\LastLoginDateReport.CSV" -NoTypeInformation -Encoding UTF8
$Result
#>


