
variable "resourcegroupname" {
  type        = string
  description = "Name of the resource group"
}


variable "aifoundryname" {
  type        = string
  description = "Name of the AI Foundry account (must be globally unique)"
  validation {
    condition     = length(var.aifoundryname) > 2
    error_message = "aifoundryname must be at least 3 characters."
  }
}

variable "project_name" {
  type        = string
  description = "Name of the AI Foundry project"
  default     = "merchDesign"
}

variable "tags" {
  description = "Tags to apply to the AI Foundry account"
  type        = map(string)
  default     = {}
}

############################################
# Model Capacity Variables
############################################
variable "gpt5_capacity" {
  type        = number
  description = "Capacity for GPT-5 deployment"
  default     = 250
  validation {
    condition     = var.gpt5_capacity > 0 && var.gpt5_capacity <= 1000
    error_message = "gpt5_capacity must be between 1 and 1000."
  }
}


variable "gpt_image_1_5_capacity" {
  type        = number
  description = "Capacity for GPT-Image-1.5 deployment"
  default     = 60
  validation {
    condition     = var.gpt_image_1_5_capacity > 0 && var.gpt_image_1_5_capacity <= 1000
    error_message = "gpt_image_1_5_capacity must be between 1 and 1000."
  }
}

variable "o3_capacity" {
  type        = number
  description = "Capacity for O3 deployment"
  default     = 250
}

############################################
# Content Filter Variables
############################################
variable "content_filters_custom" {
  type = list(object({
    name                = string
    severityThreshold   = optional(string)
    blocking            = bool
    enabled             = bool
    source              = string
  }))
  description = "Content filters for MerchDisplay-CustomFilter policy"
  default = [
    { name = "Violence", severityThreshold = "High", blocking = true, enabled = true, source = "Prompt" },
    { name = "Hate", severityThreshold = "High", blocking = true, enabled = true, source = "Prompt" },
    { name = "Sexual", severityThreshold = "High", blocking = true, enabled = true, source = "Prompt" },
    { name = "Selfharm", severityThreshold = "High", blocking = true, enabled = true, source = "Prompt" },
    { name = "Jailbreak", severityThreshold = null, blocking = false, enabled = false, source = "Prompt" },
    { name = "Indirect Attack", severityThreshold = null, blocking = false, enabled = false, source = "Prompt" },
    { name = "Violence", severityThreshold = "High", blocking = true, enabled = true, source = "Completion" },
    { name = "Hate", severityThreshold = "High", blocking = true, enabled = true, source = "Completion" },
    { name = "Sexual", severityThreshold = "High", blocking = true, enabled = true, source = "Completion" },
    { name = "Selfharm", severityThreshold = "High", blocking = true, enabled = true, source = "Completion" },
    { name = "Protected Material Text", severityThreshold = null, blocking = false, enabled = false, source = "Completion" },
    { name = "Protected Material Code", severityThreshold = null, blocking = false, enabled = false, source = "Completion" },
  ]
}

variable "public_network_access_enabled" {
  type        = bool
  description = "Enable or disable public network access to OpenAI/AI Foundry"
  default     = false
}

variable "log_analytics_workspace_id" {
  description = "Log Analytics workspace ID for Cosmos DB diagnostics"
  type        = string
}
variable "openai_location" {
  type        = string
  description = "Azure region for OpenAI Foundry deployments (e.g., swedencentral, westus3)"
  
}
