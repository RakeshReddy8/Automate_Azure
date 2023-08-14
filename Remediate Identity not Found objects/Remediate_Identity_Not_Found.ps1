#Set your Tenant Id when using Local PowerShell 
Connect-AzAccount -Tenant '<>'

$subs = Get-AzSubscription -TenantId <>

Foreach ($sub in $subs){

#Set the Subscription ID
Set-AzContext -SubscriptionId $sub.Id

#Set the Cloud File Path and Subscription Name accordingly

$FILENAME = "AzureRoles.csv"
$OBJTYPE = "Unknown"

#Find and Export-to-CSV Azure RBAC Role Assignments of 'Unknown' Type
$raunknown = Get-AzRoleAssignment | Where-Object -Property Displayname -eq $null | Export-Csv "$FILENAME" -NoClobber -NoTypeInformation -Append -Encoding UTF8 -Force


$RASTOREMOVE = Import-CSV "$FILENAME"
$RASTOREMOVE|ForEach-Object {
$object = $_.ObjectId
$roledef = $_.RoleDefinitionName
$rolescope = $_.Scope
Remove-AzRoleAssignment -ObjectId $object -RoleDefinitionName $roledef -Scope $rolescope}

}
