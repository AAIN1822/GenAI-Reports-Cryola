variable "location" {
  description = "Azure region for the Network Security Groups"
  type        = string
}

variable "resourcegroupname" {
  description = "Name of the resource group"
  type        = string
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
}

variable "environment" {
  description = "Deployment environment (e.g., dev, staging, prod)"
  type        = string
}

variable "subnets" {
  description = "Map of subnet configurations containing subnet IDs"
  type = map(object({
    subnet_id = string
  }))
}
variable "tags" {
  description = "Tags to apply to the resource group"
  type        = map(string)
  default     = {}
}
