# ============================================
# 1. Cosmos DB Account - Globally distributed NoSQL Database
# ============================================
# GlobalDocumentDB is the JSON document API (also supports MongoDB, Cassandra, Gremlin APIs)
resource "azurerm_cosmosdb_account" "fsdu_cosmos_account" {
  name                = var.cosmosdb_account_name                  # Name of the Cosmos DB account
  location            = var.location                               # Azure region for Cosmos DB
  resource_group_name = var.resourcegroupname                      # Resource group for Cosmos DB
  offer_type          = "Standard"                                # Offer type (Standard for provisioned throughput)
  kind                = "GlobalDocumentDB"                        # API kind (NoSQL JSON documents)

  public_network_access_enabled     = var.public_network_access_enabled         # Enable/disable public network access
  is_virtual_network_filter_enabled = !var.public_network_access_enabled        # Enable VNet filtering if public access is disabled

  consistency_policy {
    consistency_level = "Session"                                  # Consistency level for reads/writes
  }

  geo_location {
    location          = var.location                               # Primary region
    failover_priority = 0                                         # Failover priority (0 = primary)
  }
  tags = var.tags                                                 # Tags for resource organization

  dynamic "virtual_network_rule" {
    for_each = var.subnet_id != "" ? [var.subnet_id] : []         # Add VNet rule if subnet_id is provided
    content {
      id = virtual_network_rule.value                             # Subnet ID for VNet rule
    }
  }
}

# Retrieve account keys for outputs/secret injection
data "azurerm_cosmosdb_account" "fsdu_cosmos_account" {
  name                = azurerm_cosmosdb_account.fsdu_cosmos_account.name           # Name of the Cosmos DB account
  resource_group_name = azurerm_cosmosdb_account.fsdu_cosmos_account.resource_group_name # Resource group for Cosmos DB
}

############################################
# List Keys Action - Fetch Cosmos DB account keys
############################################
resource "azapi_resource_action" "cosmos_list_keys" {
  type        = "Microsoft.DocumentDB/databaseAccounts@2023-11-15" # Resource type for Cosmos DB account
  resource_id = azurerm_cosmosdb_account.fsdu_cosmos_account.id      # Resource ID of Cosmos DB account
  action      = "listKeys"                                          # Action to list keys
  body        = {}                                                  # Empty body for action

  response_export_values = [                                         # Keys to export
    "primaryMasterKey",
    "secondaryMasterKey",
    "primaryReadonlyMasterKey",
    "secondaryReadonlyMasterKey"
  ]
}


# ============================================
# 2. Cosmos DB SQL Database
# ============================================
# Logical container holding collections (containers) of documents
resource "azurerm_cosmosdb_sql_database" "fsdu_cosmos_sql_db" {
  name                = var.cosmos_db_name
  resource_group_name = azurerm_cosmosdb_account.fsdu_cosmos_account.resource_group_name
  account_name        = azurerm_cosmosdb_account.fsdu_cosmos_account.name
  # throughput        = 400  # Optional: shared throughput at database level (RU/s)
}

# ============================================
# 3. Cosmos DB SQL Container (Collection)
# ============================================
# Stores actual JSON documents (similar to table in relational databases)
resource "azurerm_cosmosdb_sql_container" "fsdu_cosmos_sql_container" {
  name                  = var.cosmos_sql_container_name
  resource_group_name   = azurerm_cosmosdb_account.fsdu_cosmos_account.resource_group_name
  account_name          = azurerm_cosmosdb_account.fsdu_cosmos_account.name
  database_name         = azurerm_cosmosdb_sql_database.fsdu_cosmos_sql_db.name
  partition_key_paths   = ["/myPartitionKey"]  # REQUIRED for horizontal scaling/data sharding
  partition_key_version = 2                    # Hierarchical partitioning support
  throughput            = 400                  # Provisioned RU/s (Request Units per second)
}


resource "azurerm_monitor_diagnostic_setting" "cosmos_db" {
  name                       = "cosmosdb-diagnostics"
  target_resource_id         = azurerm_cosmosdb_account.fsdu_cosmos_account.id
  log_analytics_workspace_id = var.log_analytics_workspace_id

  enabled_log {
    category = "DataPlaneRequests"
  }

  enabled_log {
    category = "ControlPlaneRequests"
  }

  metric {
    category = "AllMetrics"
    enabled  = true

  }
}
