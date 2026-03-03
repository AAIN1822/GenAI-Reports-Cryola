variable "name" {
  type        = string
  description = "Name of the Application Insights or Log Analytics Workspace resource"
}

variable "location" {
  type        = string
  description = "Azure location for the resource"
}

variable "resourcegroupname" {
  type        = string
  description = "Resource group to deploy Application Insights or Log Analytics"
}

variable "application_type" {
  type        = string
  default     = "web"
  description = "Application type for App Insights (web, other)"
}

variable "tags" {
  type        = map(string)
  description = "Tags to apply to resources"
}

variable "sku" {
  type        = string
  default     = "PerGB2018"
  description = "The pricing tier for Log Analytics Workspace"
}

variable "retention_in_days" {
  type        = number
  default     = 30
  description = "Retention period for Log Analytics Workspace (in days)"
}
// variable "acr_id" {
//     type        = string
//     description = "The ID of the Azure Container Registry to monitor"
// }
// variable "cosmos_id" {
//     type        = string
//     description = "The ID of the Cosmos DB account to monitor" 
// }
// variable "keyvault_id" {
//     type        = string
//     description = "The ID of the Key Vault to monitor"
  
// }
// variable "aifoundry_id" {
//     type        = string
//     description = "The ID of the AI Foundry to monitor"
  
// }
// variable "storage_account_id" {
//     type        = string
//     description = "The ID of the Storage Account to monitor"
  
// }
// variable "container_app_id" {
//     type        = string
//     description = "The ID of the Container App to monitor"
  
// }
// variable "container_environment_id" {
//     type        = string
//     description = "The ID of the Container App Environment to monitor"
// }
