variable "apim_name" {
    type        = string
    description = "Name of the API Management instance"
    validation {
        condition     = length(var.apim_name) > 2
        error_message = "apim_name must be at least 3 characters."
    }
}
variable "subnet_id" {
    type        = string
    description = "ID of the subnet to deploy API Management into"
  
}
variable "aifoundry_id" {
    type        = string
    description = "Resource ID of the AI Foundry deployment for role assignment scope"
  
}
variable "resourcegroupname" {
    type        = string
    description = "Resource group to deploy API Management"
    validation {
        condition     = length(var.resourcegroupname) > 2
        error_message = "resourcegroupname must be at least 3 characters."
    }
}
variable "location" {
    type        = string
    description = "Azure location for the API Management instance"
}
variable "publisher_name" {
    type        = string
    description = "Publisher name for the API Management instance"
}
variable "publisher_email" {
    type        = string
    description = "Publisher email for the API Management instance"
}
variable "sku_name" {
    type        = string
    description = "SKU name for API Management (Developer, Basic, Standard, Premium)"
    validation {
        condition     = contains(["Developer_1", "Basic", "Standard", "Premium"], var.sku_name)
        error_message = "sku_name must be one of: Developer_1, Basic, Standard, Premium."
    }
}
variable "tags" {
    type        = map(string)
    description = "Tags to apply to the API Management instance"
}


variable "aifoundryname" {
    type        = string
    description = "Name of the AI Foundry deployment"
}

variable "api_name" {
    type        = string
    description = "Name of the API to create in API Management"
  
}
# variable "secondary_backend_url" {
#     type        = string
#     description = "Secondary backend URL for the API (optional)"

# }
variable "aifoundry_endpoint" {
    type        = string
    description = "Endpoint URL of the AI Foundry deployment"

  
}

variable "subscription_id" {
    type        = string
    description = "Azure Subscription ID for role assignment scope"
}

variable "service_principal_client_id" {
    type        = string
    description = "Client/Application ID of the service principal (service connection) for role assignment"
}