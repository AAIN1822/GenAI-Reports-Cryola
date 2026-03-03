output "appinsights_instrumentation_key" {
  value = azurerm_application_insights.appinsights.instrumentation_key
}
output "connection_string" {
  value = azurerm_application_insights.appinsights.connection_string
}
