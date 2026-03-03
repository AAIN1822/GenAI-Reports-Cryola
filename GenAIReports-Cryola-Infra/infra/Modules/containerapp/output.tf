output "container_app_id" {
  value       = azurerm_container_app.fsdu_con_app.id
  description = "Container App ID"
}

output "container_app_name" {
  value       = azurerm_container_app.fsdu_con_app.name
  description = "Container App name"
}

output "container_app_fqdn" {
  value       = azurerm_container_app.fsdu_con_app.ingress[0].fqdn
  description = "Container App FQDN"
}

output "principal_id" {
  value       = azurerm_container_app.fsdu_con_app.identity[0].principal_id
  description = "Container App principal ID"
}
output "container_app_environment_id" {
  value       = azurerm_container_app_environment.fsdu_con_env.id
  description = "Container App Environment ID"
  
}
