variable "private_endpoint_dependency" {
  description = "Resource or list of resources to depend on for private endpoint creation."
  type        = any
  default     = null
}
variable "container_app_principal_id" {
  description = "The principal ID of the Container App managed identity"
  type        = string
}
variable "keyvaultname" {
  description = "The name of the Key Vault (must be globally unique)"
  type        = string
}

variable "location" {
  description = "The location of the Key Vault"
  type        = string
}

variable "resourcegroupname" {
  description = "The name of the Resource Group where the Key Vault will be created"
  type        = string
}

variable "tenant_id" {
  description = "The Tenant ID for the Key Vault access policies (sensitive)"
  type        = string
  sensitive   = true
}

variable "object_id" {
  description = "The Object ID for the Key Vault access policy - typically a service principal or user (sensitive)"
  type        = string
  sensitive   = true
}

variable "terraform_sp_object_id" {
  description = "The Object ID of the Terraform service principal that needs access to manage secrets (sensitive)"
  type        = string
  sensitive   = true
  default     = ""
}

// variable "secrets" {
//   description = "Map of secrets to store in Key Vault. Key is the secret name, value is the secret value"
//   type        = map(string)
//   default     = {}
// }

variable "keyvault_subnet_ids" {
  description = "List of subnet IDs for KeyVault network rules (optional, for future lockdown)"
  type        = list(string)
  default     = []
}
variable "tags" {
  description = "Tags to apply to the resource group"
  type        = map(string)
  default     = {}
}

variable "public_network_access_enabled" {
  type        = bool
  description = "Enable or disable public network access to Key Vault"
  default     = false
}

variable "log_analytics_workspace_id" {
  description = "Log Analytics workspace ID for Cosmos DB diagnostics"
  type        = string
}