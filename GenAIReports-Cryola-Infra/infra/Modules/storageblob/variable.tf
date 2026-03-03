variable "storageaccountid" {
  type        = string
  description = "The ID of the storage account"
}

variable "storage_account_name" {
  type        = string
  description = "The name of the storage account"
}

variable "storagecontainername" {
  type        = string
  description = "Name of the storage blob container to create or reference"
}

variable "create_container" {
  type        = bool
  description = "Whether to create the storage container (true) or reference existing (false)"
  default     = true
}

variable "private_endpoint_dependency" {
  type        = list(string)
  description = "List of private endpoint resource IDs to depend on for creation ordering"
  default     = []
}