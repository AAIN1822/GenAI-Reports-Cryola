variable "subnet_id" {
  description = "The ID of the subnet to attach Cosmos DB to (e.g., storage subnet)"
  type        = string
}
variable "location" {
  description = "The location of the Cosmos DB account"
  type        = string
}


variable "resourcegroupname" {
  description = "The name of the Resource Group where the Cosmos DB account will be created"
  type        = string
}

variable "cosmos_db_name" {
  description = "The name of the Cosmos DB NoSQL database"
  type        = string
}

variable "cosmos_sql_container_name" {
  description = "The name of the Cosmos DB NoSQL container"
  type        = string
}

variable "cosmosdb_account_name" {
  type        = string
  description = "The name of the Cosmos DB Account (must be globally unique)"
}
variable "tags" {
  description = "Tags to apply to the resource group"
  type        = map(string)
  default     = {}
}

variable "public_network_access_enabled" {
  type        = bool
  description = "Enable or disable public network access to Cosmos DB"
  default     = false
}
variable "log_analytics_workspace_id" {
  description = "Log Analytics workspace ID for Cosmos DB diagnostics"
  type        = string
}
