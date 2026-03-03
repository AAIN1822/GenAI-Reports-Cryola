output "storage_container_name" {
  value = var.create_container ? azurerm_storage_container.fsdu_storage_blob_container[0].name : null
}

output "storage_container_id" {
  value = var.create_container ? azurerm_storage_container.fsdu_storage_blob_container[0].id : null
}
