#Set the Tenant Id and Subscription Name
Connect-AzAccount -Tenant ''
Set-AzContext -SubscriptionName ''

#Set the path of the CSV Data file
$groups    = (Import-Csv 'C:\Users\rakes\Azure_Group.csv').groups | ?{$_ -ne ''}
$rgs       = (Import-Csv 'C:\Users\rakes\Azure_Group.csv').resourcegroups | ?{$_ -ne ''}
$RoleNames = (Import-Csv 'C:\Users\rakes\Azure_Group.csv').rolenames | ?{$_ -ne ''}

foreach ($RoleName in $RoleNames){
	foreach ($rg in $rgs){
		foreach ($group in $groups){
			$ObjectID = ($group)
			New-AzRoleAssignment -ObjectId $ObjectID `
			-RoleDefinitionName $RoleName `
			-ResourceGroupName $rg
			}
			}
			}
