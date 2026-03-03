output "stored_secrets" {
  value       = keys(azurerm_key_vault_secret.fsdu_secrets)
  description = "List of stored secret names"
}