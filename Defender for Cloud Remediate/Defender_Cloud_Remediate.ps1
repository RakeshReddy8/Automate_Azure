Connect-AzAccount -Tenant ''

Set-AzContext -Subscription ""

$Response = Search-AzGraph -Query "SecurityResources `
| where type == 'microsoft.security/assessments' `
| where properties.displayName contains 'Deprecated accounts should be removed from subscriptions' `
| where subscriptionId == '' `
| extend Ids=properties.additionalData.deprecatedAccountsObjectIdList `
| project tenantId, subscriptionId, Ids"

$ss=$Response.Ids -split "[]"",""[]" -ne ""

ForEach($Id in $ss){
	
	$Details = Get-AzRoleAssignment -ObjectId $Id
	$Details
	$Details.SignInName | Get-Unique
	$Scope = $Details.Scope	| Get-Unique
	
	$UserAccountDetails = [ordered]@{
                      
					  #UserPrincipalName = $Details.SignInName | Get-Unique
					  Scope = $Details.Scope | Get-Unique
					  RoleDefinitionNames = ($Details.RoleDefinitionName -join ',')
	}
	
	$UserAccountDetails | Export-Csv testdisk.csv -NoClobber -NoTypeInformation -Append -Encoding UTF8 -Force
	
	ForEach($Role in $Details.RoleDefinitionName){
		$Role
		
		Remove-AzRoleAssignment -ObjectId $Id `
		-RoleDefinitionName $Role `
		-Scope $Scope
		}
		
		
$storageAccountName = "automationdeprecated"

$storageAccount = Get-AzStorageAccount -ResourceGroupName "cloud-shell-storage-centralindia" -Name $storageAccountName

$ctx = $storageAccount.Context

$tableName = "pshtesttable"
#New-AzStorageTable –Name $tableName –Context $ctx

$storageTable = Get-AzStorageTable –Name $tableName –Context $ctx

$cloudTable = $storageTable.CloudTable

#[string]$PartKey = $Details.DisplayName | Get-Unique
[string]$PartKey = $Details.ObjectType | Get-Unique 
[string]$RowKey = $Details.ObjectId | Get-Unique

Add-AzTableRow `
    -table $cloudTable `
    -partitionKey $PartKey `
    -rowKey $RowKey -property $UserAccountDetails
	
}
