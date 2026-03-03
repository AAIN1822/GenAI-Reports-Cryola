output "cosmosdb_account_name" {
  value = azurerm_cosmosdb_account.fsdu_cosmos_account.name
}
output "cosmosdb_account_id" {
  value = azurerm_cosmosdb_account.fsdu_cosmos_account.id
}
output "cosmosdb_sql_database_id" {
  value = azurerm_cosmosdb_sql_database.fsdu_cosmos_sql_db.id
}
output "cosmosdb_sql_container_id" {
  value = azurerm_cosmosdb_sql_container.fsdu_cosmos_sql_container.id
}

# Primary key (master key) for the Cosmos DB account
output "cosmosdb_primary_master_key" {
  value     = try(azapi_resource_action.cosmos_list_keys.output.primaryMasterKey, "")
  sensitive = true
}

output "cosmosdb_secondary_master_key" {
  value     = try(azapi_resource_action.cosmos_list_keys.output.secondaryMasterKey, "")
  sensitive = true
}

output "cosmosdb_primary_readonly_master_key" {
  value     = try(azapi_resource_action.cosmos_list_keys.output.primaryReadonlyMasterKey, "")
  sensitive = true
}

output "cosmosdb_secondary_readonly_master_key" {
  value     = try(azapi_resource_action.cosmos_list_keys.output.secondaryReadonlyMasterKey, "")
  sensitive = true
}

