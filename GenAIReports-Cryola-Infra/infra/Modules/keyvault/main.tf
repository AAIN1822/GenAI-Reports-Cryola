# Key Vault - Secure storage for secrets, keys, and certificates
resource "azurerm_key_vault" "fsdu_keyvault" {
  name                = var.keyvaultname
  location            = var.location
  resource_group_name = var.resourcegroupname
  tenant_id           = var.tenant_id    # Entra ID tenant for authentication

  sku_name                      = "standard"    # Standard tier for application secrets
  purge_protection_enabled      = false         # Allow purge for development (enable in production)
  public_network_access_enabled = var.public_network_access_enabled  # Disable public access
  soft_delete_retention_days    = 7             # Recover deleted secrets within 7 days
  # rbac_authorization_enabled     = true         # RBAC preferred over legacy access policies

  network_acls {
    default_action             = var.public_network_access_enabled ? "Allow" : "Deny"  # Deny all public traffic
    bypass                     = "AzureServices"           # Allow Azure platform services access
    virtual_network_subnet_ids = var.keyvault_subnet_ids  # Restrict to private endpoints
  }
  tags = var.tags
}

# ----------------------------
# Access Policy for Terraform Service Principal
# ----------------------------
resource "azurerm_key_vault_access_policy" "terraform_sp" {
  count = var.terraform_sp_object_id != "" ? 1 : 0

  key_vault_id       = azurerm_key_vault.fsdu_keyvault.id
  tenant_id          = var.tenant_id
  object_id          = var.terraform_sp_object_id

  secret_permissions = ["Get", "List", "Set", "Delete", "Purge"]
}
resource "azurerm_key_vault_access_policy" "container_app" {
  key_vault_id = azurerm_key_vault.fsdu_keyvault.id
  tenant_id    = var.tenant_id
  object_id    = var.container_app_principal_id

  secret_permissions = ["Get", "List", "Set", "Delete", "Recover", "Backup", "Restore"]
}
# ----------------------------
# RBAC Role Assignment for Current User
# ----------------------------
resource "azurerm_role_assignment" "current_user_kv_access" {
  scope              = azurerm_key_vault.fsdu_keyvault.id
  role_definition_name = "Key Vault Secrets Officer"
  principal_id       = var.object_id
}


resource "azurerm_monitor_diagnostic_setting" "keyvault" {
  name                       = "kv-diagnostics"
  target_resource_id         = azurerm_key_vault.fsdu_keyvault.id
  log_analytics_workspace_id = var.log_analytics_workspace_id

  enabled_log {
    category = "AuditEvent"
  }

  metric {
    category = "AllMetrics"
    enabled  = true
  }

  depends_on = [
    azurerm_key_vault.fsdu_keyvault
  ]
}


