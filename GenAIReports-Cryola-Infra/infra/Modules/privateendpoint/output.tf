output "private_endpoint_ids" {
  value = {
    for k, pe in azurerm_private_endpoint.fsdu_private_endpoint :
    k => pe.id
  }
}

output "private_endpoint_names" {
  value = {
    for k, pe in azurerm_private_endpoint.fsdu_private_endpoint :
    k => pe.name
  }
}
