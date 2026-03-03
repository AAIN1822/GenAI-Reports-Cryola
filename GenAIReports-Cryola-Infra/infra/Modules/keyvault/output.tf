output "keyvault_id" {
  value       = azurerm_key_vault.fsdu_keyvault.id
  description = "The ID of the Key Vault"
}

output "keyvault_uri" {
  value       = azurerm_key_vault.fsdu_keyvault.vault_uri
  description = "The URI of the Key Vault"
}

output "keyvault_name" {
  value       = azurerm_key_vault.fsdu_keyvault.name
  description = "The name of the Key Vault"
}
