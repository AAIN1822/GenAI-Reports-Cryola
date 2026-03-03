variable "rg_prefixes" {
  description = "Prefixes for each resource group (e.g., network, storage, backend, frontend, monitor, infra, ai)"
  type        = map(string)
}

variable "location" {
  description = "Primary Azure region for resource deployment"
  type        = string
}

variable "tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default     = {}
}

variable "environment" {
  description = "Deployment environment name (e.g., dev, staging, prod)"
  type        = string
}

variable "subnets" {
  description = "Map of subnet configurations for VNet"
  type = map(object({
    address_prefixes = list(string)
  }))
}

variable "address_space" {
  description = "Address space for the VNet (e.g., [\"10.0.0.0/16\"])"
  type        = list(string)
}

variable "windows_vm_name" {
  description = "Name of the Windows VM."
  type        = string
  default     = "bootstrap-vm"
}

variable "windows_vm_admin_username" {
  description = "Admin username for the Windows VM."
  type        = string
  default     = "Crayola"
}

variable "windows_vm_admin_password" {
  description = "Admin password for the Windows VM."
  type        = string
  sensitive   = true
  default     = "Crayola@123456"
}
variable "project_name" {
  description = "Project name to use in resource naming"
  type        = string
  
}
