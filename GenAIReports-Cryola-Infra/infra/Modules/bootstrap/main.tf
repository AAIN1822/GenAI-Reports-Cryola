

module "ResourceGroup" {
  source            = "../resourcegroup"
  for_each          = var.rg_prefixes
  resourcegroupname = "rg-${var.project_name}-${each.value}-${var.environment}"
  location          = var.location
  tags              = var.tags
}

module "VirtualNetwork" {
  source            = "../virtualnetwork"
  depends_on        = [module.ResourceGroup]
  vnetname          = "vnet-${var.project_name}-${var.environment}"
  resourcegroupname = module.ResourceGroup["network"].rgname
  location          = module.ResourceGroup["network"].location
  address_space     = var.address_space
  subnets           = var.subnets
  environment       = var.environment
  project_name      = var.project_name
  tags              = var.tags
}

module "nsg" {
  source            = "../nsg"
  depends_on        = [module.VirtualNetwork]
  location          = module.ResourceGroup["network"].location
  resourcegroupname = module.ResourceGroup["network"].rgname
  project_name      = var.project_name
  environment       = var.environment
  subnets           = module.VirtualNetwork.subnets
  tags              = var.tags
}

module "windowsvm" {
  source              = "../windowsvm"
  vm_name             = var.windows_vm_name
  resource_group_name = module.ResourceGroup["infra"].rgname
  location            = module.ResourceGroup["infra"].location
  vm_size             = "Standard_B2ms"
  admin_username      = var.windows_vm_admin_username
  admin_password      = var.windows_vm_admin_password
  subnet_id           = module.VirtualNetwork.subnets["infra"].subnet_id
  depends_on          = [module.VirtualNetwork, module.nsg]
}
