output "vnet_id" {
  value = azurerm_virtual_network.fsdu_vnet.id
}

output "subnet_ids" {
  value = { for k, v in azurerm_subnet.fsdu_subnet : k => v.id }
}
output "subnets" {
  value = {
    for k, s in azurerm_subnet.fsdu_subnet :
    k => {
      subnet_id = s.id
      name      = s.name
      key       = k
    }
  }
}

