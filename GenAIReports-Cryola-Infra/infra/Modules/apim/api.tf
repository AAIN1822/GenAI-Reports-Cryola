resource "azurerm_api_management_api" "container" {
  name                = "container-api"
  resource_group_name = var.resourcegroupname
  api_management_name = azurerm_api_management.apim.name
  revision            = "1"
  display_name        = "Container App API"
  path                = "container"
  protocols           = ["https"]
  service_url         = var.aifoundry_endpoint

  import {
    content_format = "openapi"
    content_value  = file("${path.module}/openapi.yaml")
  }
}

resource "azurerm_api_management_api_policy" "container_policy" {
  api_name            = azurerm_api_management_api.container.name
  api_management_name = azurerm_api_management.apim.name
  resource_group_name = var.resourcegroupname

  xml_content = <<XML
<policies>
  <inbound>
    <base />
    <!-- CORS Policy (standard, minimal) -->
    <cors>
      <allowed-origins>
        <origin>*</origin>
      </allowed-origins>
      <allowed-methods>
        <method>GET</method>
        <method>POST</method>
        <method>OPTIONS</method>
      </allowed-methods>
      <allowed-headers>
        <header>*</header>
      </allowed-headers>
    </cors>
    <!-- Remove or configure validate-jwt and rate-limit only if you have correct values and supported tier -->
    <!-- <validate-content max-size="1048576" /> -->
  </inbound>
  <backend>
    <base />
  </backend>
  <outbound>
    <base />
  </outbound>
  <on-error>
    <base />
  </on-error>
</policies>
XML
}