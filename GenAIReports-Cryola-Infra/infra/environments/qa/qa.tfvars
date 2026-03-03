rg_prefixes = {
  network  = "networking"
  storage  = "storage"
  backend  = "backend"
  frontend = "frontend"
  monitor  = "monitoring"
  infra    = "infra"
  ai       = "ai"
  apim     = "apim"
}

location    = "eastus2"
environment = "qa02"

tags = {
  owner = "infraTeam"
  env   = "qa02"
  mode = "terraform"
}


## NETWORKING components
address_space = ["10.10.2.0/25"]
subnets = {
  backend  = { address_prefixes = ["10.10.2.0/27"] }
  network  = { address_prefixes = ["10.10.2.32/28"] }
  storage  = { address_prefixes = ["10.10.2.48/28"] }
  frontend = { address_prefixes = ["10.10.2.64/28"] }
  monitor  = { address_prefixes = ["10.10.2.80/28"] }
  infra    = { address_prefixes = ["10.10.2.96/28"] }
  ai       = { address_prefixes = ["10.10.2.112/28"] }
}

##Storage account
storage_account_tier     = "Standard"
account_replication_type = "LRS"

## Container app
cpu                      = 2
memory                   = "4Gi"
image_revision_suffix    = "v1"

# AI Foundry Model Capacities
gpt5_capacity           = 250
gpt_image_1_5_capacity  = 10
o3_capacity         = 100


# Key Vault Secrets (example - update with your actual secrets)
keyvault_secrets = {
  "secret-key"            = "supersecretkey"
  "microsoft-client-id"   = "763a51ad-2799-4644-bb30-932457d18517"
  "microsoft-tenant-id"   = "d271cff8-4452-47ec-b61f-e20ed50d0bc7"

}

# Windows VM credentials for bootstrap
windows_vm_admin_username = "azureadmin"
windows_vm_admin_password = "P@ssw0rd123!"  # Change this to a secure password

## APIM 
apim_sku = "Developer_1"

## OpenAI Foundry deployment location
openai_location = "swedencentral"  # Region for AI Foundry deployments (GPT-5, O3, etc.)

# Backend configuration for Terraform remote state
backend_resource_group_name  = "sf-terraform-storage"   # Resource group for remote state
backend_storage_account_name = "sfterraformsaeus"       # Storage account for remote state
backend_container_name       = "con-terraform"          # Blob container for remote state
backend_key                  = "bootstrap-qa.tfstate"  