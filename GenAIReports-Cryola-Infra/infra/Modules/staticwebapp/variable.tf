variable "resourcegroupname" {
  description = "Name of the resource group"
  type        = string
}

variable "location" {
  description = "Azure region for the static web app"
  type        = string
}
variable "tags" {
  description = "Tags to apply to the resource group"
  type        = map(string)
  default     = {}
}
variable "static_web_app_name" {
  description = "Name of the static web app resource"
  type        = string
}
