resource "azurerm_key_vault_secret" "fsdu_secrets" {
  for_each     = var.secrets           # Iterate over each secret

  name         = each.key             # Name of the secret
  value        = each.value           # Value of the secret
  key_vault_id = var.keyvault_id      # Key Vault ID to store the secret
}