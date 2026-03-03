# APIM Gateway URL (Container App calls this)
output "apim_gateway_url" {
  value = azurerm_api_management.apim.gateway_url
}

# APIM Managed Identity principal ID
output "apim_principal_id" {
  value = azurerm_api_management.apim.identity[0].principal_id
}

# Backend ID for reference
output "ai_backend_id" {
  value = azurerm_api_management_backend.ai_backend.id
}