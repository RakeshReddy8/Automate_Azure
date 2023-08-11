$Objs = Import-Excel -Path "C:\Users\reddkov\Downloads\Guest Acceptance 2 (9).xlsx" -WorksheetName "Azure Trusts" | ?{$_ -ne ''}

$ActiveDirectoryList=@()

foreach($user in $Objs) {

    $userRealmUriFormat = "https://login.microsoftonline.com/common/userrealm?user={urlEncodedMail}&api-version=2.1"

    $encodedMail = [System.Web.HttpUtility]::UrlEncode($User.defaultDomainName)
    
    $userRealmUri = $userRealmUriFormat -replace "{urlEncodedMail}", $encodedMail
    Write-Verbose $userRealmUri

    $userRealmResponse = Invoke-WebRequest -Uri $userRealmUri
    $content = ConvertFrom-Json ($userRealmResponse)
    
    $isExternalAzureADViral = ($content.IsViral) -eq "True"


$ActiveDirectoryObject = New-Object PSObject
$ActiveDirectoryObject | Add-Member -MemberType NoteProperty -Name tenantid -Value $user.tenantid
$ActiveDirectoryObject | Add-Member -MemberType NoteProperty -Name displayName -Value $user.displayName
$ActiveDirectoryObject | Add-Member -MemberType NoteProperty -Name defaultDomainName -Value $user.defaultDomainName
$ActiveDirectoryObject | Add-Member -MemberType NoteProperty -Name isExternalAzureADViral -Value $isExternalAzureADViral
$ActiveDirectoryList += $ActiveDirectoryObject

}

$ActiveDirectoryList | Export-CSV "C:\temp\ViralTenantCheckExport.CSV" -NoTypeInformation