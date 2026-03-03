resource "azurerm_application_insights" "appinsights" {
  name                     = var.name                                 # Name of the Application Insights resource
  location                 = var.location                             # Azure region for Application Insights
  resource_group_name      = var.resourcegroupname                    # Resource group for Application Insights
  application_type         = var.application_type                     # Application type ("web" for web/container apps)
  workspace_id             = var.log_analytics_workspace_id           # Log Analytics workspace ID
  tags                     = var.tags                                # Tags for resource organization
}