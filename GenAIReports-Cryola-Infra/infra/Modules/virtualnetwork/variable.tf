variable "vnetname" {
  description = "Name of the virtual network"
  type        = string
}

variable "resourcegroupname" {
  description = "Resource group name for the VNet"
  type        = string
}

variable "location" {
  description = "Location of the VNet"
  type        = string
}

variable "address_space" {
  description = "Address space for the VNet (e.g., [\"10.0.0.0/16\"])"
  type        = list(string)
}

variable "subnets" {
  description = "Map of subnet configurations with address prefixes"
  type = map(object({
    address_prefixes = list(string)
  }))
}

variable "tags" {
  description = "Tags for the VNet"
  type        = map(string)
}

variable "environment" {
  description = "Deployment environment (e.g., dev, staging, prod)"
  type        = string
}

variable "project_name" {
  description = "Project name for resource naming convention"
  type        = string
}
