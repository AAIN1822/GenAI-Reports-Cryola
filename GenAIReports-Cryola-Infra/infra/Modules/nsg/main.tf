# Network Security Group - Created but no rules (allow all for testing)
resource "azurerm_network_security_group" "fsdu_nsg" {
  for_each            = var.subnets                                         # Iterate over each subnet
  name                = "nsg-${var.project_name}-${each.key}-${var.environment}" # Name of the NSG
  location            = var.location                                       # Azure region for NSG
  resource_group_name = var.resourcegroupname                              # Resource group for NSG
  tags                = var.tags                                           # Tags for resource organization
}

# Associate NSG with each subnet
resource "azurerm_subnet_network_security_group_association" "fsdu_nsg_association" {
  for_each                  = var.subnets                                         # Iterate over each subnet
  depends_on                = [azurerm_network_security_group.fsdu_nsg]           # Ensure NSG is created first
  subnet_id                 = each.value.subnet_id                                # Subnet ID to associate
  network_security_group_id = azurerm_network_security_group.fsdu_nsg[each.key].id # NSG ID to associate
}

# NOTE: All NSG rules have been removed for testing Container App deployment.
# Once deployment succeeds, re-add the security rules:
# - Backend: DNS (53), HTTP (80), HTTPS (443), Azure Services, Metadata Service (169.254.169.254:80)
# - Storage/AI/Frontend: DNS (53), HTTPS (443), inbound from backend

# Allow WinRM (5985) for VM provisioning
resource "azurerm_network_security_rule" "allow_winrm" {
  for_each                    = var.subnets                                         # Iterate over each subnet
  name                        = "allow_winrm"                                      # Name of the rule
  priority                    = 1001                                                # Rule priority
  direction                   = "Inbound"                                           # Inbound rule
  access                      = "Allow"                                             # Allow traffic
  protocol                    = "Tcp"                                               # TCP protocol
  source_port_range           = "*"                                                 # Any source port
  destination_port_range      = "5985"                                              # WinRM port
  source_address_prefix       = "*"                                                 # Any source address
  destination_address_prefix  = "*"                                                 # Any destination address
  resource_group_name         = var.resourcegroupname                                # Resource group for rule
  network_security_group_name = azurerm_network_security_group.fsdu_nsg[each.key].name # NSG name for rule
}

# Allow RDP (3389) for VM connectivity
resource "azurerm_network_security_rule" "allow_rdp" {
  for_each                    = var.subnets                                         # Iterate over each subnet
  name                        = "allow_rdp"                                        # Name of the rule
  priority                    = 1002                                                # Rule priority
  direction                   = "Inbound"                                           # Inbound rule
  access                      = "Allow"                                             # Allow traffic
  protocol                    = "Tcp"                                               # TCP protocol
  source_port_range           = "*"                                                 # Any source port
  destination_port_range      = "3389"                                              # RDP port
  source_address_prefix       = "*"                                                 # Any source address
  destination_address_prefix  = "*"                                                 # Any destination address
  resource_group_name         = var.resourcegroupname                                # Resource group for rule
  network_security_group_name = azurerm_network_security_group.fsdu_nsg[each.key].name # NSG name for rule
}

# Allow APIM management endpoint (3443) for VNet integration
resource "azurerm_network_security_rule" "allow_apim_management" {
  for_each                    = var.subnets                                         # Iterate over each subnet
  name                        = "allow_apim_management"
  priority                    = 1003
  direction                   = "Inbound"
  access                      = "Allow"
  protocol                    = "Tcp"
  source_port_range           = "*"
  destination_port_range      = "3443"
  source_address_prefix       = "*"
  destination_address_prefix  = "*"
  resource_group_name         = var.resourcegroupname
  network_security_group_name = azurerm_network_security_group.fsdu_nsg[each.key].name
}

# Allow outbound HTTPS (443) for internet access (Azure DevOps agent download, etc.)
resource "azurerm_network_security_rule" "allow_outbound_https" {
  for_each                    = var.subnets                                         # Iterate over each subnet
  name                        = "allow_outbound_https"                             # Name of the rule
  priority                    = 1000                                                # Rule priority
  direction                   = "Outbound"                                          # Outbound rule
  access                      = "Allow"                                             # Allow traffic
  protocol                    = "Tcp"                                               # TCP protocol
  source_port_range           = "*"                                                 # Any source port
  destination_port_range      = "443"                                               # HTTPS port
  source_address_prefix       = "*"                                                 # Any source address
  destination_address_prefix  = "Internet"                                          # Internet destination
  resource_group_name         = var.resourcegroupname                                # Resource group for rule
  network_security_group_name = azurerm_network_security_group.fsdu_nsg[each.key].name # NSG name for rule
}

# Allow outbound DNS (53) for name resolution
resource "azurerm_network_security_rule" "allow_outbound_dns" {
  for_each                    = var.subnets                                         # Iterate over each subnet
  name                        = "allow_outbound_dns"                               # Name of the rule
  priority                    = 1001                                                # Rule priority
  direction                   = "Outbound"                                          # Outbound rule
  access                      = "Allow"                                             # Allow traffic
  protocol                    = "*"                                                 # Any protocol
  source_port_range           = "*"                                                 # Any source port
  destination_port_range      = "53"                                                # DNS port
  source_address_prefix       = "*"                                                 # Any source address
  destination_address_prefix  = "Internet"                                          # Internet destination
  resource_group_name         = var.resourcegroupname                                # Resource group for rule
  network_security_group_name = azurerm_network_security_group.fsdu_nsg[each.key].name # NSG name for rule
}
