terraform {
  backend "azurerm" {
    resource_group_name  = var.backend_resource_group_name  # Resource group for remote state
    storage_account_name = var.backend_storage_account_name  # Storage account for remote state
    container_name       = var.backend_container_name       # Blob container for remote state
    key                  = var.backend_key                  # State file key
  }
}

