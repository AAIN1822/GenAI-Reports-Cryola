variable "enable_registry" {
  type        = bool
  description = "Enable registry block for container app (set false for first apply, true for second)"
  default     = true
}
variable "appinsights_connection_string" {
   type        = string
   description = "Application Insights connection string for telemetry."
 }
variable "container_environment_name" {
  type        = string
  description = "Name of the container app environment"
}

variable "container_app_name" {
  type        = string
  description = "Name of the container app"
}

variable "container_name" {
  type        = string
  description = "Name of the container"
}

variable "location" {
  type        = string
  description = "Azure region"
}

variable "resourcegroupname" {
  type        = string
  description = "Resource group name"
}

variable "subnet_id" {
  type        = string
  description = "Subnet ID for container app environment"
}

variable "cpu" {
  type        = number
  description = "CPU allocation (0.5, 1, 2)"
}

variable "memory" {
  type        = string
  description = "Memory allocation (0.5Gi, 1Gi, 2Gi)"
}


variable "container_image" {
  type        = string
  description = "Full container image URL (public: mcr.microsoft.com/azuredocs/containerapps-helloworld:latest, or ACR: myacr.azurecr.io/app:latest)"
}

variable "acr_id" {
  type        = string
  description = "ACR resource ID"
}

variable "storage_account_id" {
  type        = string
  description = "Storage account resource ID"
}

variable "cosmos_id" {
  type        = string
  description = "Cosmos DB resource ID"
}

variable "ai_foundry_id" {
  type        = string
  description = "OpenAI resource ID"
}

variable "tags" {
  type        = map(string)
  description = "Tags"
  default     = {}
}

variable "image_revision_suffix" {
  type        = string
  description = "Revision suffix to force new deployment when image changes (e.g., image tag or timestamp). If not set, uses current timestamp."
  default     = ""
}


variable "internal_load_balancer_enabled" {
  type        = bool
  description = "Enable internal load balancer for private Container App (no public endpoint)"
  default     = false
}
variable "acr_login_server" {
  type        = string
  description = "ACR login server URL (e.g., myacr.azurecr.io)"
}

# APIM gateway URL to be used as the OpenAI endpoint
variable "apim_gateway_url" {
  type        = string
  description = "APIM gateway URL to be used as the OpenAI endpoint for all OpenAI API calls."
  default     = ""
}
