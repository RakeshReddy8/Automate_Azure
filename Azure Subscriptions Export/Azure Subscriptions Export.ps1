Connect-AzAccount

$storageAccounts = Get-AzSubscription
        
  [System.Collections.ArrayList]$saUsage = New-Object -TypeName System.Collections.ArrayList
        
   foreach ($storageAccount in $storageAccounts) {
        
        
              $StorageAccountDetails = [ordered]@{
                      
                      Subscription_Name = $storageAccount.Name
					  Subscription_Id = $storageAccount.Id
					  Tenant_Id = $storageAccount.TenantId
					  State = $storageAccount.State
					                           
                }
               $saUsage.add((New-Object psobject -Property $StorageAccountDetails))  | Out-Null   
  }
  
  $saUsage | Export-Csv -Path C:\temp\Subscription_List.csv -NoClobber -NoTypeInformation -Encoding UTF8 -Force
  