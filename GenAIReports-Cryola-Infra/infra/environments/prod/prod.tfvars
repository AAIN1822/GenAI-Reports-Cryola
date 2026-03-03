rg_prefixes = {
  network  = "networking"
  storage  = "storage"
  backend  = "backend"
  frontend = "frontend"
  monitor  = "monitoring"
  infra    = "infra"
  ai       = "ai"
}

location    = "eastus2"
environment = "prod"

tags = {
  owner = "infraTeam"
  env   = "prod"
  mode = "terraform"
}

address_space = ["10.0.0.0/16"]
subnets = {
  network  = { address_prefixes = ["10.0.1.0/24"] }
  storage  = { address_prefixes = ["10.0.2.0/24"] }
  backend  = { address_prefixes = ["10.0.4.0/23"] }
  frontend = { address_prefixes = ["10.0.6.0/24"] }
  monitor  = { address_prefixes = ["10.0.7.0/24"] }
  infra    = { address_prefixes = ["10.0.8.0/24"] }
  ai       = { address_prefixes = ["10.0.9.0/24"] }
  
}


storage_account_tier     = "Standard"
account_replication_type = "LRS"
cpu                      = 2
memory                   = "4Gi"
acr_image_name           = "mcr.microsoft.com/k8se/quickstart:latest"
image_revision_suffix    = "v1"

# AI Foundry Model Capacities
gpt5_capacity           = 250
gpt_image_1_5_capacity  = 60
o3_capacity         = 250


# Key Vault Secrets (example - update with your actual secrets)
keyvault_secrets = {
  "secret-key"            = "supersecretkey"
  "microsoft-client-id"   = "763a51ad-2799-4644-bb30-932457d18517"
  "microsoft-tenant-id"   = "d271cff8-4452-47ec-b61f-e20ed50d0bc7"

}

# Windows VM credentials for bootstrap
windows_vm_admin_username = "azureadmin"
windows_vm_admin_password = "P@ssw0rd123!"  # Change this to a secure password