
# Name of the container registry (must be globally unique, lowercase alphanumeric only)
variable "acr_name" {
  type        = string
  description = "Name of the container registry (must be globally unique, lowercase alphanumeric only)"
  validation {
    condition     = can(regex("^[a-z0-9]{5,50}$", var.acr_name))
    error_message = "acr_name must be 5-50 chars, lowercase alphanumeric only."
  }
}


# Azure region where the container registry will be created
variable "location" {
  type        = string
  description = "Azure region for the container registry"
}


# Name of the resource group where the container registry will be created
variable "resourcegroupname" {
  type        = string
  description = "Name of the resource group where the container registry will be created"
}


# Tags to apply to the container registry for resource organization
variable "tags" {
  type        = map(string)
  description = "Tags to apply to the container registry"
}


# SKU of the container registry (Basic, Standard, Premium)
variable "sku" {
  type        = string
  description = "SKU of the container registry (Basic, Standard, Premium)"
  default     = "Premium"
  validation {
    condition     = contains(["Basic", "Standard", "Premium"], var.sku)
    error_message = "sku must be one of: Basic, Standard, Premium."
  }
}


# Whether the admin user is enabled for the registry (not recommended for production)
variable "admin_enabled" {
  type        = bool
  description = "Whether the admin user is enabled for the registry"
  default     = false
}


# Enable zone redundancy for the registry where supported (for high availability)
variable "zone_redundancy_enabled" {
  type        = bool
  description = "Enable zone redundancy for the registry where supported"
  default     = true
}


# Allow public network access to the registry (set to false for private access only)
variable "public_network_access_enabled" {
  type        = bool
  description = "Allow public network access to the registry"
  default     = true
}

# Log Analytics workspace ID for ACR diagnostics and monitoring
variable "log_analytics_workspace_id" {
  description = "Log Analytics workspace ID for Cosmos DB diagnostics"
  type        = string
}

