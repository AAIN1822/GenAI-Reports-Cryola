output "acr_id" {
  value       = azurerm_container_registry.fsdu_acr.id
  description = "ACR resource ID"
}

output "acr_name" {
  value       = azurerm_container_registry.fsdu_acr.name
  description = "ACR name"
}

output "acr_login_server" {
  value       = azurerm_container_registry.fsdu_acr.login_server
  description = "ACR login server URL for image pulls"
}
