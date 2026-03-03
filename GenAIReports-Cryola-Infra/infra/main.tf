data "azurerm_client_config" "current" {}
  # Retrieves current subscription and tenant context

# =============================================================================
# REMOTE STATE - Reference outputs from bootstrap configuration
# =============================================================================
# Bootstrap creates ResourceGroup, VirtualNetwork, NSG, and WindowsVM
# We read those outputs from the shared state file

module "bootstrap" {
  source              = "./Modules/bootstrap"                  # Path to bootstrap module
  rg_prefixes         = var.rg_prefixes                        # Prefixes for resource groups
  location            = var.location                           # Azure region for deployment
  tags                = var.tags                               # Common tags for resources
  project_name        = local.project_name                     # Project name
  environment         = var.environment                        # Deployment environment
  subnets             = var.subnets                            # Subnet configurations
  address_space       = var.address_space                      # VNet address space
  windows_vm_name     = var.windows_vm_name                    # Windows VM name
  windows_vm_admin_username = var.windows_vm_admin_username    # Windows VM admin username
  windows_vm_admin_password = var.windows_vm_admin_password    # Windows VM admin password
}

# Local aliases for cleaner references
locals {
  # Resource Groups from bootstrap
  rg_network  = module.bootstrap.resource_groups["network"]   # Network RG
  rg_storage  = module.bootstrap.resource_groups["storage"]   # Storage RG
  rg_backend  = module.bootstrap.resource_groups["backend"]   # Backend RG
  rg_frontend = module.bootstrap.resource_groups["frontend"]  # Frontend RG
  rg_ai       = module.bootstrap.resource_groups["ai"]        # AI RG
  rg_infra    = module.bootstrap.resource_groups["infra"]     # Infra RG
  rg_monitor  = module.bootstrap.resource_groups["monitor"]   # Monitor RG
  rg_apim     = module.bootstrap.resource_groups["apim"]      # APIM RG

  # VNet and Subnets from bootstrap
  vnet_id = module.bootstrap.vnet_id                           # VNet ID
  subnets = module.bootstrap.subnets                           # Subnets map

  # Unique revision suffix for container app
  unique_revision_suffix = formatdate("YYYYMMDDhhmmss", timestamp()) # Unique suffix
}

# =============================================================================
# RESOURCES - Created by this configuration (runs on self-hosted agent)
# =============================================================================

module "storageaccount" {
  source                   = "./Modules/storageaccount"
  storageaccountname       = "strge${local.project_name}${var.environment}"
  location                 = local.rg_storage.location
  resourcegroupname        = local.rg_storage.name
  account_tier             = var.storage_account_tier
  account_replication_type = var.account_replication_type
  tags                     = var.tags
  log_analytics_workspace_id = module.loganalytics.workspace_id
}

module "storage_blob_container" {
  source                      = "./Modules/storageblob"
  storagecontainername        = "container-${local.project_name}-${var.environment}"
  storageaccountid            = module.storageaccount.storage_account_id
  storage_account_name        = module.storageaccount.storage_account_name
  create_container            = true
  private_endpoint_dependency = [module.private_endpoints.private_endpoint_ids["storage_blob_pe"]]

  depends_on = [module.storageaccount, module.private_endpoints]
}

module "keyvault" {
  source            = "./Modules/keyvault"
  depends_on        =[module.containerapp]
  keyvaultname      = "kvlt${local.project_name}${var.environment}"
  resourcegroupname = local.rg_storage.name
  location          = local.rg_storage.location
  tenant_id         = data.azurerm_client_config.current.tenant_id
  object_id         = data.azurerm_client_config.current.object_id
  terraform_sp_object_id     = data.azurerm_client_config.current.object_id
  container_app_principal_id = module.containerapp.principal_id
  keyvault_subnet_ids        = [local.subnets["storage"].subnet_id]
  public_network_access_enabled = false
  tags = var.tags
  log_analytics_workspace_id  = module.loganalytics.workspace_id
}

module "secrets" {
  source = "./Modules/secrets"
  keyvault_id = module.keyvault.keyvault_id
  secrets = merge(
    var.keyvault_secrets,
    {
      "cosmos-key" = module.cosmosdb.cosmosdb_primary_master_key
      "azure-openai-api-key" = module.openai.aifoundry_primary_access_key
    }
  )
  depends_on = [ module.private_endpoints ]
}

  module "apim" {
    source                = "./Modules/apim"
    api_name              = "api-${local.project_name}-${var.environment}"
    apim_name            = "apim-${local.project_name}-${var.environment}"
    location              = local.rg_apim.location
    resourcegroupname     = local.rg_apim.name
    publisher_name        = "Company"
    publisher_email       = "r@example.com"
    sku_name              = "Developer_1"
    aifoundryname         = module.openai.aifoundry_name 
    subnet_id             = local.subnets["infra"].subnet_id
    aifoundry_id         = module.openai.openai_account_id
    tags                  = var.tags
  #  secondary_backend_url = "https://${module.containerapp.container_app_default_hostname}" # Secondary backend URL for APIM (Container App)
    aifoundry_endpoint = module.openai.aifoundry_endpoint
    subscription_id = data.azurerm_client_config.current.subscription_id
    service_principal_client_id = data.azurerm_client_config.current.client_id
  }
module "cosmosdb" {
  source                    = "./Modules/cosmosdb"
  cosmos_db_name            = "cosmosdb-${local.project_name}-${var.environment}"
  cosmosdb_account_name     = "cosmos-${local.project_name}-${var.environment}"
  resourcegroupname         = local.rg_storage.name
  location                  = local.rg_storage.location
  cosmos_sql_container_name = "dbcontainer-${local.project_name}-${var.environment}"
  tags                      = var.tags
  subnet_id                 = local.subnets["storage"].subnet_id
  log_analytics_workspace_id  = module.loganalytics.workspace_id
}

module "acr" {
  source            = "./Modules/acr"
  acr_name          = "acr${local.project_name}${var.environment}"
  resourcegroupname = local.rg_storage.name
  location          = local.rg_storage.location
  tags              = var.tags
  log_analytics_workspace_id = module.loganalytics.workspace_id
}

module "containerapp" {
  source                     = "./Modules/containerapp"
  depends_on                 = [module.acr, module.cosmosdb, module.storageaccount, module.openai, module.appinsights]
  container_environment_name = "con-env-${local.project_name}-${var.environment}"
  container_app_name         = "con-app-${local.project_name}-${var.environment}"
  container_name             = "conapp-${local.project_name}-${var.environment}"
  resourcegroupname          = local.rg_backend.name
  location                   = local.rg_backend.location
  subnet_id                  = local.subnets["backend"].subnet_id
  cpu                        = var.cpu
  memory                     = var.memory
  tags                       = var.tags
  acr_id                     = module.acr.acr_id
  cosmos_id                  = module.cosmosdb.cosmosdb_account_id
  storage_account_id         = module.storageaccount.storage_account_id
  ai_foundry_id              = module.openai.openai_account_id
  container_image            = format("%s/nginx:latest", module.acr.acr_login_server)
  image_revision_suffix      = local.unique_revision_suffix
  acr_login_server           = module.acr.acr_login_server
  appinsights_connection_string = module.appinsights.connection_string
  apim_gateway_url           = module.apim.apim_gateway_url # Pass APIM gateway URL to container app for OpenAI API calls
}

module "staticwebapp" {
  source              = "./Modules/staticwebapp"
  static_web_app_name = "staticwebapp-${local.project_name}-${var.environment}"
  resourcegroupname   = local.rg_frontend.name
  location            = local.rg_frontend.location
  tags = var.tags
}

module "loganalytics" {
  source              = "./Modules/loganalytics"
  name                = "loganalytics-${local.project_name}-${var.environment}"
  location            = local.rg_monitor.location
  resourcegroupname   = local.rg_monitor.name
  retention_in_days   = 30
  tags                = var.tags 
}
module "appinsights" {
  source              = "./Modules/appinsights"
  name                = "appinisght-${local.project_name}-${var.environment}"
  location            = local.rg_monitor.location
  resourcegroupname   = local.rg_monitor.name
  application_type    = "web"
  log_analytics_workspace_id = module.loganalytics.workspace_id
  tags                        = var.tags
  depends_on = [
    module.loganalytics
  ]
}

  module "openai" {
    source = "./Modules/openai"
    depends_on = [module.appinsights]
    aifoundryname       = "aifoundry-${local.project_name}-${var.environment}"
    project_name        = "merchDesign"
    resourcegroupname   = local.rg_ai.name
    openai_location     = var.openai_location
    gpt5_capacity           = var.gpt5_capacity
    gpt_image_1_5_capacity  = var.gpt_image_1_5_capacity
    o3_capacity         = var.o3_capacity
    tags = var.tags
    log_analytics_workspace_id  = module.loganalytics.workspace_id
  }

module "private_endpoints" {
  source            = "./Modules/privateendpoint"
  depends_on        = [module.storageaccount, module.cosmosdb, module.keyvault, module.acr, module.openai]
  location            = local.rg_network.location
  resourcegroupname   = local.rg_network.name
  vnet_id             = local.vnet_id
  tags = var.tags
  private_endpoints = {
    keyvault_pe = {
      name              = "pe-${local.project_name}-keyvault-${var.environment}"
      subnet_id         = local.subnets["storage"].subnet_id
      resource_id       = module.keyvault.keyvault_id
      subresource_names = ["vault"]
    }

    storage_blob_pe = {
      name              = "pe-${local.project_name}-storageblob-${var.environment}"
      subnet_id         = local.subnets["storage"].subnet_id
      resource_id       = module.storageaccount.storage_account_id
      subresource_names = ["blob"]
    }

    cosmos_pe = {
      name              = "pe-${local.project_name}-cosmosdb-${var.environment}"
      subnet_id         = local.subnets["storage"].subnet_id
      resource_id       = module.cosmosdb.cosmosdb_account_id
      subresource_names = ["Sql"]
    }

    openai_pe = {
      name              = "pe-${local.project_name}-openai-${var.environment}"
      subnet_id         = local.subnets["ai"].subnet_id
      resource_id       = module.openai.openai_account_id
      subresource_names = ["account"]
    }

  }
}

