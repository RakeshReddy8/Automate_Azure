Connect-AzAccount -Identity

Set-AzContext -Subscription ""

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
$ApiUrl = "https://graph.microsoft.com/beta/users?`$select=displayName,userPrincipalName,signInActivity,userType,assignedLicenses,accountEnabled&`$top=999"
 
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
IsGuestUser  = if ($User.userType -eq 'Guest') { $true } else { $false }
IsAccountEnabled = $User.accountEnabled
})
}
 
}
$ApiUrl=$Response.'@odata.nextlink'
}

#Un-Comment the below if you want the full sign-in logs report
$Result | Export-CSV "LastLoginDateReport.CSV" -NoTypeInformation -Encoding UTF8

<#
$DaysInactive = 60
$dateTime = (Get-Date).Adddays(-($DaysInactive))
$Result | Where-Object { $_.LastSignInDateTime -eq $Null -OR $_.lastNonInteractiveSignInDateTime -eq $Null -OR ($_.LastSignInDateTime -le $dateTime -and $_.lastNonInteractiveSignInDateTime -le $dateTime)} | Export-CSV "C:\Temp\LastLoginDateReport.CSV" -NoTypeInformation -Encoding UTF8
$Result
#>

Set-AzCurrentStorageAccount -ResourceGroupName "cloud-shell-storage-centralindia" -Name "automationdeprecated"
Set-AzStorageBlobContent -Container "test" -File "LastLoginDateReport.CSV" -Blob "users.csv" -Force