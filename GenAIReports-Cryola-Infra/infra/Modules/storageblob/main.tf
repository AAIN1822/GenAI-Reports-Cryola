resource "azurerm_storage_container" "fsdu_storage_blob_container" {
  count                 = var.create_container ? 1 : 0         # Create resource only if create_container is true
  name                  = var.storagecontainername             # Name of the storage container
  storage_account_name  = var.storage_account_name              # Name of the parent storage account
  container_access_type = "private"                            # Access type for the container (private, blob, container)
}