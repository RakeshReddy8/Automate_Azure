$SubscriptionIds = Get-Content -Path "path for SubscriptionID.txt"  
Foreach($SubscriptionId in $SubscriptionIds)
{
	Set-AzContext -SubscriptionId $SubscriptionId


$context = Get-AzContext
        
  $storageAccounts = Get-AzDisk
        
  [System.Collections.ArrayList]$saUsage = New-Object -TypeName System.Collections.ArrayList
        
   foreach ($storageAccount in $storageAccounts) {
        
        
              $StorageAccountDetails = [ordered]@{
                      
                      Disk_Name = $storageAccount.Name
					  SKU_Name = $storageAccount.sku.name
					  DiskSizeGB = $storageAccount.DiskSizeGB
					  Owner = $storageAccount.managedBy
					  ResourceGroupName = $storageAccount.ResourceGroupName
					  Location = $storageAccount.Location
					  SubscriptionName = $context.Subscription.Name
                      Disk_Tier = $storageAccount.Tier
					  
                }
               $saUsage.add((New-Object psobject -Property $StorageAccountDetails))  | Out-Null   
  }
  $saUsage | Export-Csv -Path C:\Users\rakes\qptestdisk.csv -NoClobber -NoTypeInformation -Append -Encoding UTF8 -Force
}