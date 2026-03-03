resource "azurerm_resource_group" "fsdu-rg" {
  name     = var.resourcegroupname      # Name of the resource group
  location = var.location              # Azure region for the resource group
  tags     = var.tags                  # Tags for resource organization
}