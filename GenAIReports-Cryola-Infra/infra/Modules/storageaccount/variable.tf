variable "storageaccountname" {
  description = "Name of the storage account (must be globally unique, lowercase alphanumeric only)"
  type        = string
}

variable "location" {
  description = "Azure region for the storage account"
  type        = string
}

variable "resourcegroupname" {
  description = "Name of the resource group"
  type        = string
}

variable "account_tier" {
  type        = string
  description = "Storage account tier: Standard or Premium"
}

variable "account_replication_type" {
  type        = string
  description = "Replication type: LRS (Locally Redundant), GRS (Geo-Redundant), RAGRS (Read-access Geo-Redundant), ZRS (Zone-Redundant)"
}

variable "tags" {
  type        = map(string)
  description = "Tags to apply to the storage account"
  default     = {}
}



variable "network_bypass" {
  description = "Bypass traffic for specified Azure services. Options: None, AzureServices, Logging, Metrics"
  type        = list(string)
  default     = ["AzureServices"]
}

variable "network_default_action" {
  description = "The default action of allow or deny when no other rules match. Possible values are Deny and Allow"
  type        = string
  default     = "Allow"

  validation {
    condition     = contains(["Allow", "Deny"], var.network_default_action)
    error_message = "network_default_action must be either Allow or Deny."
  }
}

variable "public_network_access_enabled" {
  type        = bool
  description = "Enable or disable public network access to the storage account"
  default     = false
}

variable "log_analytics_workspace_id" {
  description = "Log Analytics workspace ID for Cosmos DB diagnostics"
  type        = string
}