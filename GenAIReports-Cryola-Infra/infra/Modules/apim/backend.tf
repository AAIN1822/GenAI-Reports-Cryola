resource "azurerm_api_management_backend" "ai_backend" {
  name                = "ai-backend"
  resource_group_name = var.resourcegroupname
  api_management_name = azurerm_api_management.apim.name
  protocol            = "http"
  url                 = var.aifoundry_endpoint
}