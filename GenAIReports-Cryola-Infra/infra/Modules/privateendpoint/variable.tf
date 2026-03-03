variable "location" {
  description = "Azure region for private endpoints"
  type        = string
}

variable "resourcegroupname" {
  description = "Name of the resource group"
  type        = string
}

variable "vnet_id" {
  description = "Virtual Network ID for DNS zone linking"
  type        = string
}

variable "private_endpoints" {
  description = "Map of private endpoints to create with their configurations"
  type = map(object({
    name              = string
    subnet_id         = string
    resource_id       = string
    subresource_names = list(string)
  }))
}
variable "tags" {
  description = "Tags to apply to the resource group"
  type        = map(string)
  default     = {}
}