# Azure Static Web App - Globally distributed frontend hosting with CDN and authentication
resource "azurerm_static_web_app" "fsdu_static_web_app" {
  name                = var.static_web_app_name      # Name of the static web app (DNS: {name}.azurestaticapps.net)
  resource_group_name = var.resourcegroupname        # Resource group for the static web app
  location            = var.location                 # Azure region (must be eastus2 for Static Web Apps)
  tags                = var.tags                     # Tags for resource organization
}