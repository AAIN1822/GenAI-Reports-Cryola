resource "azurerm_storage_account" "fsdu_storage" {
  name                     = var.storageaccountname                  # Name of the storage account
  location                 = var.location                            # Azure region for the storage account
  resource_group_name      = var.resourcegroupname                   # Resource group for the storage account
  account_tier             = var.account_tier                        # Storage account tier (Standard or Premium)
  account_replication_type = var.account_replication_type            # Replication type (LRS, GRS, ZRS)

  allow_nested_items_to_be_public = false                            # Block all public blob access
  min_tls_version                 = "TLS1_2"                        # Enforce TLS 1.2+ encryption in transit
  public_network_access_enabled   = var.public_network_access_enabled # Enable/disable public network access

  network_rules {
    default_action = var.public_network_access_enabled ? "Allow" : "Deny" # Allow or deny public traffic
    bypass         = ["AzureServices"]                                 # Allow Azure services (Terraform, monitoring)
  }

  tags = var.tags                                              # Tags for resource organization
}

resource "azurerm_monitor_diagnostic_setting" "storage_diagnostics" {
  name                       = "storage-diagnostics"                        # Name of the diagnostic setting
  target_resource_id         = azurerm_storage_account.fsdu_storage.id       # Resource ID of the storage account
  log_analytics_workspace_id = var.log_analytics_workspace_id                # Log Analytics workspace for diagnostics

  metric {
    category = "Capacity"    # Collect capacity metrics
    enabled  = true           # Enable metric collection
  }

  metric {
    category = "Transaction" # Collect transaction metrics
    enabled  = true           # Enable metric collection
  }

  depends_on = [
    azurerm_storage_account.fsdu_storage                # Ensure storage account is created first
  ]
}

