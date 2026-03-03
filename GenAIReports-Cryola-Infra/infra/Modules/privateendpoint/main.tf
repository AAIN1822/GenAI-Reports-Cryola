resource "azurerm_private_endpoint" "fsdu_private_endpoint" {
  for_each            = var.private_endpoints                        # Iterate over each private endpoint definition
  name                = each.value.name                              # Name of the private endpoint
  location            = var.location                                 # Azure region for the private endpoint
  resource_group_name = var.resourcegroupname                        # Resource group for the private endpoint
  subnet_id           = each.value.subnet_id                         # Subnet ID for the private endpoint

  private_service_connection {
    name                           = "${each.value.name}-pe-conn"           # Name of the private service connection
    private_connection_resource_id = each.value.resource_id                  # Resource ID to connect privately
    subresource_names              = each.value.subresource_names            # Subresources for the connection
    is_manual_connection           = false                                   # Use automatic connection
  }
  tags = var.tags                                              # Tags for resource organization
}

# Private DNS Zones for each endpoint type
resource "azurerm_private_dns_zone" "keyvault_dns" {
  name                = "privatelink.vaultcore.azure.net"           # DNS zone for Key Vault private endpoint
  resource_group_name = var.resourcegroupname                        # Resource group for DNS zone
}

resource "azurerm_private_dns_zone" "storage_dns" {
  name                = "privatelink.blob.core.windows.net"         # DNS zone for Storage private endpoint
  resource_group_name = var.resourcegroupname                        # Resource group for DNS zone
}

resource "azurerm_private_dns_zone" "cosmos_dns" {
  name                = "privatelink.documents.azure.com"           # DNS zone for Cosmos DB private endpoint
  resource_group_name = var.resourcegroupname                        # Resource group for DNS zone
}

resource "azurerm_private_dns_zone" "openai_dns" {
  name                = "privatelink.cognitiveservices.azure.com"   # DNS zone for OpenAI private endpoint
  resource_group_name = var.resourcegroupname                        # Resource group for DNS zone
}
resource "azurerm_private_dns_zone" "openai" {
  name                = "privatelink.openai.azure.com"
  resource_group_name = var.resourcegroupname
}
// Removed ACR private DNS zone

# Link DNS zones to VNet
resource "azurerm_private_dns_zone_virtual_network_link" "keyvault_dns_link" {
  name                  = "keyvault-dns-link"                        # Name of the DNS zone link
  resource_group_name   = var.resourcegroupname                       # Resource group for DNS link
  private_dns_zone_name = azurerm_private_dns_zone.keyvault_dns.name  # DNS zone name
  virtual_network_id    = var.vnet_id                                 # VNet ID to link
}

resource "azurerm_private_dns_zone_virtual_network_link" "storage_dns_link" {
  name                  = "storage-dns-link"                         # Name of the DNS zone link
  resource_group_name   = var.resourcegroupname                       # Resource group for DNS link
  private_dns_zone_name = azurerm_private_dns_zone.storage_dns.name   # DNS zone name
  virtual_network_id    = var.vnet_id                                 # VNet ID to link
}

resource "azurerm_private_dns_zone_virtual_network_link" "cosmos_dns_link" {
  name                  = "cosmos-dns-link"                          # Name of the DNS zone link
  resource_group_name   = var.resourcegroupname                       # Resource group for DNS link
  private_dns_zone_name = azurerm_private_dns_zone.cosmos_dns.name    # DNS zone name
  virtual_network_id    = var.vnet_id                                 # VNet ID to link
}

resource "azurerm_private_dns_zone_virtual_network_link" "openai_dns_link" {
  name                  = "openai-dns-link"
  resource_group_name   = var.resourcegroupname
  private_dns_zone_name = azurerm_private_dns_zone.openai_dns.name
  virtual_network_id    = var.vnet_id
}

resource "azurerm_private_dns_zone_virtual_network_link" "openai_link" {
  name                  = "openai-link"
  resource_group_name   = var.resourcegroupname
  private_dns_zone_name = azurerm_private_dns_zone.openai.name
  virtual_network_id    = var.vnet_id
}

// Removed ACR DNS zone VNet link

# DNS A records for each private endpoint
resource "azurerm_private_dns_a_record" "keyvault_record" {
  for_each            = { for k, pe in azurerm_private_endpoint.fsdu_private_endpoint : k => pe if k == "keyvault_pe" }
  name                = "*"
  zone_name           = azurerm_private_dns_zone.keyvault_dns.name
  resource_group_name = var.resourcegroupname
  ttl                 = 300
  records             = [azurerm_private_endpoint.fsdu_private_endpoint["keyvault_pe"].private_service_connection[0].private_ip_address]
}

resource "azurerm_private_dns_a_record" "storage_record" {
  for_each            = { for k, pe in azurerm_private_endpoint.fsdu_private_endpoint : k => pe if k == "storage_blob_pe" }
  name                = "*"
  zone_name           = azurerm_private_dns_zone.storage_dns.name
  resource_group_name = var.resourcegroupname
  ttl                 = 300
  records             = [azurerm_private_endpoint.fsdu_private_endpoint["storage_blob_pe"].private_service_connection[0].private_ip_address]
}

resource "azurerm_private_dns_a_record" "cosmos_record" {
  for_each            = { for k, pe in azurerm_private_endpoint.fsdu_private_endpoint : k => pe if k == "cosmos_pe" }
  name                = "*"
  zone_name           = azurerm_private_dns_zone.cosmos_dns.name
  resource_group_name = var.resourcegroupname
  ttl                 = 300
  records             = [azurerm_private_endpoint.fsdu_private_endpoint["cosmos_pe"].private_service_connection[0].private_ip_address]
}

resource "azurerm_private_dns_a_record" "openai_record" {
  for_each            = { for k, pe in azurerm_private_endpoint.fsdu_private_endpoint : k => pe if k == "openai_pe" }
  name                = "*"
  zone_name           = azurerm_private_dns_zone.openai_dns.name
  resource_group_name = var.resourcegroupname
  ttl                 = 300
  records             = [azurerm_private_endpoint.fsdu_private_endpoint["openai_pe"].private_service_connection[0].private_ip_address]
}



