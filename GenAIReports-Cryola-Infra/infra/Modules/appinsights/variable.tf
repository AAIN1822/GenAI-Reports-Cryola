variable "name" {
  type        = string
  description = "Name of the Application Insights or Log Analytics Workspace resource"
}

variable "location" {
  type        = string
  description = "Azure location for the resource"
}

variable "resourcegroupname" {
  type        = string
  description = "Resource group to deploy Application Insights or Log Analytics"
}

variable "application_type" {
  type        = string
  default     = "web"
  description = "Application type for App Insights (web, other)"
}

variable "tags" {
  type        = map(string)
  description = "Tags to apply to resources"
}
variable "log_analytics_workspace_id" {
  type        = string
  description = "Optional Log Analytics workspace ID to link App Insights"
  
}
