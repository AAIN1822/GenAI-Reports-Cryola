resource "azurerm_log_analytics_workspace" "loganalytics" {
  name                     = var.name                                 # Name of the Log Analytics workspace
  location                 = var.location                             # Azure region for Log Analytics
  resource_group_name      = var.resourcegroupname                    # Resource group for Log Analytics
  sku                     = var.sku                                  # SKU for Log Analytics (PerGB, Standard, etc.)
  retention_in_days        = var.retention_in_days                    # Data retention in days
  tags                     = var.tags                                # Tags for resource organization
}





