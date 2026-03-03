output "vm_id" {
  value = azurerm_windows_virtual_machine.this.id
}
output "vm_private_ip" {
  value = azurerm_network_interface.this.private_ip_address
}
