Connect-AzAccount

$value = Get-AzAccessToken -ResourceUrl "https://graph.microsoft.com/"

$value.Token
