# Windows VM Module
resource "azurerm_windows_virtual_machine" "this" {
  name                  = var.vm_name                                 # Name of the VM
  resource_group_name   = var.resource_group_name                     # Resource group for the VM
  location              = var.location                                # Azure region for the VM
  size                  = var.vm_size                                 # VM size (SKU)
  admin_username        = var.admin_username                          # Admin username for the VM
  admin_password        = var.admin_password                          # Admin password for the VM
  network_interface_ids = [azurerm_network_interface.this.id]          # Network interface for the VM
  os_disk {
    caching              = "ReadWrite"                                # Disk caching mode
    storage_account_type = "Standard_LRS"                            # Storage type for OS disk
  }
  source_image_reference {
    publisher = "MicrosoftWindowsServer"                             # Image publisher
    offer     = "WindowsServer"                                      # Image offer
    sku       = "2022-datacenter"                                   # Image SKU
    version   = "latest"                                            # Image version
  }
  provision_vm_agent       = true                                     # Install VM agent
  patch_mode               = "AutomaticByOS"                        # Enable automatic patching
}

resource "azurerm_public_ip" "this" {
  name                = "${var.vm_name}-pip"                # Name of the public IP resource
  location            = var.location                        # Azure region for the public IP
  resource_group_name = var.resource_group_name              # Resource group for the public IP
  allocation_method   = "Static"                            # Static allocation method
  sku                 = "Standard"                          # SKU for the public IP
}

resource "azurerm_network_interface" "this" {
  name                = "${var.vm_name}-nic"                # Name of the network interface
  location            = var.location                        # Azure region for the NIC
  resource_group_name = var.resource_group_name              # Resource group for the NIC
  ip_configuration {
    name                          = "internal"              # Name of the IP configuration
    subnet_id                     = var.subnet_id           # Subnet ID for the NIC
    private_ip_address_allocation = "Dynamic"               # Dynamic private IP allocation
    public_ip_address_id          = azurerm_public_ip.this.id # Associate public IP
  }
}

locals {
  # Bootstrap script - install CLI first, then agent (so agent has CLI in PATH)
  bootstrap_commands = join(" ; ", [
    "$ProgressPreference='SilentlyContinue'", # Suppress progress bar
    "[Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12", # Use TLS 1.2
    "New-Item -ItemType Directory -Force -Path 'C:\\agent' | Out-Null", # Create agent directory
    "Set-Location 'C:\\agent'", # Change to agent directory
    # Install Azure CLI FIRST (before agent, so agent service sees it in PATH)
    "(New-Object Net.WebClient).DownloadFile('https://aka.ms/installazurecliwindowsx64','C:\\agent\\AzureCLI.msi')", # Download Azure CLI installer
    "Start-Process msiexec.exe -ArgumentList '/i','C:\\agent\\AzureCLI.msi','/quiet','/norestart' -Wait", # Install Azure CLI
    # Download Azure DevOps agent
    "(New-Object Net.WebClient).DownloadFile('https://download.agent.dev.azure.com/agent/4.266.2/vsts-agent-win-x64-4.266.2.zip','C:\\agent\\agent.zip')", # Download DevOps agent
    "Add-Type -A System.IO.Compression.FileSystem", # Add compression type
    "[IO.Compression.ZipFile]::ExtractToDirectory('C:\\agent\\agent.zip','C:\\agent')", # Extract agent
    "Start-Sleep 5", # Wait for service
    "Get-Service vstsagent* | Start-Service -EA SilentlyContinue" # Start agent service
  ])
}

resource "azurerm_virtual_machine_extension" "agent_bootstrap" {
  name                 = "agent-bootstrap"                                 # Name of the extension
  virtual_machine_id   = azurerm_windows_virtual_machine.this.id            # VM to attach the extension
  publisher            = "Microsoft.Compute"                               # Publisher of the extension
  type                 = "CustomScriptExtension"                           # Type of extension
  type_handler_version = "1.10"                                            # Handler version

  settings = jsonencode({
    commandToExecute = "powershell -ExecutionPolicy Bypass -Command \"${local.bootstrap_commands}; exit 0\"" # Command to execute
  })
}
