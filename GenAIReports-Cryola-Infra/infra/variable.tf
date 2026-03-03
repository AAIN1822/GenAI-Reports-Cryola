# Prefixes for each resource group (e.g., network, storage, backend, frontend, monitor, infra, ai)
variable "rg_prefixes" {
  description = "Prefixes for each resource group (e.g., network, storage, backend, frontend, monitor, infra, ai)"
  type        = map(string)
}

# Primary Azure region for resource deployment
variable "location" {
  description = "Primary Azure region for resource deployment"
  type        = string
}

# Common tags to apply to all resources
variable "tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default     = {}
}

# Deployment environment name (e.g., dev, staging, prod)
variable "environment" {
  description = "Deployment environment name (e.g., dev, staging, prod)"
  type        = string
}

# Map of subnet configurations for VNet
variable "subnets" {
  description = "Map of subnet configurations for VNet"
  type = map(object({
    address_prefixes = list(string)
  }))
}

# Address space for the VNet (e.g., ["10.0.0.0/16"])
variable "address_space" {
  description = "Address space for the VNet (e.g., [\"10.0.0.0/16\"])"
  type        = list(string)
}

# Storage account tier: Standard or Premium
variable "storage_account_tier" {
  description = "Storage account tier: Standard or Premium"
  type        = string
}

# Storage account replication type: LRS, GRS, RAGRS, ZRS
variable "account_replication_type" {
  description = "Storage account replication type: LRS, GRS, RAGRS, ZRS"
  type        = string
}

# CPU allocation for the container app in cores
variable "cpu" {
  description = "CPU allocation for the container app in cores"
  type        = number
}

# Memory allocation for the container app (e.g., "2Gi", "1Gi")
variable "memory" {
  description = "Memory allocation for the container app (e.g., \"2Gi\", \"1Gi\")"
  type        = string
}


# variable "acr_image_name" {
#   description = "Production container image name/tag in ACR (e.g., myapp:latest or myapp:v1.0.0)"
#   type        = string
# }



variable "keyvault_secrets" {
  description = "Map of secrets to store in Key Vault. Key is the secret name, value is the secret value"
  type        = map(string)

}


variable "image_revision_suffix" {
  description = "Image revision suffix to force container app update (e.g., v1.0.0, latest, or build number)"
  type        = string
  default     = ""
}

############################################
# AI Foundry Model Capacity Variables
############################################
variable "gpt5_capacity" {
  type        = number
  description = "Capacity for GPT-5 deployment"
  default     = 250
}


variable "gpt_image_1_5_capacity" {
  type        = number
  description = "Capacity for GPT-Image-1.5 deployment"
  default     = 60
}

variable "o3_capacity" {
  type        = number
  description = "Capacity for O3 deployment"
  default     = 250
}

# Windows VM variables
variable "windows_vm_name" {
  description = "Name of the Windows VM."
  type        = string
  default     = "bootstrap-vm"
}

variable "windows_vm_admin_username" {
  description = "Admin username for the Windows VM."
  type        = string
}

variable "windows_vm_admin_password" {
  description = "Admin password for the Windows VM."
  type        = string
  sensitive   = true
}
variable "apim_sku" {
  description = "SKU for API Management service (e.g., Consumption, Developer, Basic, Standard, Premium)"
  type        = string
  default     = "Developer"
  
}

variable "backend_resource_group_name" {
    type        = string
    description = "Resource group name for the API Management backend service (e.g., OpenAI Foundry or Container App)"
  
}
variable "backend_storage_account_name" {
    type        = string
    description = "Storage account name for the API Management backend service (if needed)"
  
}
variable "backend_container_name" {
    type        = string
    description = "Container name for the API Management backend service (if needed)"
  
}
variable "backend_key" {
    type        = string
    description = "Key for the API Management backend service state file in remote storage" 
}
variable "openai_location" {
  type        = string
  description = "Azure region for OpenAI Foundry deployments (e.g., swedencentral, westus3)"
}