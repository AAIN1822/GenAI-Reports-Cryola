output "resource_groups" {
  description = "Map of resource groups with name, location, and id"
  value = {
    for k, v in module.ResourceGroup : k => {
      name     = v.rgname
      location = v.location
      id       = v.id
    }
  }
}

output "vnet_id" {
  description = "ID of the Virtual Network"
  value       = module.VirtualNetwork.vnet_id
}

output "subnets" {
  description = "Map of subnets with id and name"
  value       = module.VirtualNetwork.subnets
}
