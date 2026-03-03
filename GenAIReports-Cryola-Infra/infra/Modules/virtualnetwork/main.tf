# Virtual Network - Isolated network for secure internal communication
resource "azurerm_virtual_network" "fsdu_vnet" {
  name                = var.vnetname              # Name of the Virtual Network
  location            = var.location              # Azure region for the VNet
  resource_group_name = var.resourcegroupname     # Resource group where VNet will be created
  address_space       = var.address_space         # Address space for the VNet (e.g., 10.0.0.0/16)
  tags                = var.tags                  # Tags for resource organization
}

# Subnets - Logical segmentation by workload/security requirements (backend, storage, ai, etc)
resource "azurerm_subnet" "fsdu_subnet" {
  for_each             = var.subnets                                         # Iterate over each subnet definition
  name                 = "snet-${var.project_name}-${each.key}-${var.environment}" # Subnet name pattern
  resource_group_name  = var.resourcegroupname                              # Resource group for subnet
  virtual_network_name = azurerm_virtual_network.fsdu_vnet.name             # Parent VNet name
  address_prefixes     = each.value.address_prefixes                        # Address prefixes for the subnet

  private_endpoint_network_policies = "Disabled"                            # Allow private endpoints without policy restrictions
  service_endpoints = ["Microsoft.KeyVault", "Microsoft.AzureCosmosDB"]    # Enable service endpoints for KeyVault and CosmosDB

  lifecycle {
    ignore_changes = [
      delegation                                                        # Ignore changes to delegation block
    ]
  }

  dynamic "delegation" {
    for_each = each.key == "backend" ? [1] : []                          # Delegate only for backend subnet
    content {
      name = "aca_delegation"                                           # Delegation name
      service_delegation {
        name = "Microsoft.App/environments"                             # Delegate to Azure Container Apps
        actions = [
          "Microsoft.Network/virtualNetworks/subnets/action"            # Required action for ACA
        ]
      }
    }
  }
}

