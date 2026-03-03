terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"   # Provider source
      version = "~> 3.110.0"          # Provider version constraint
    }

    azapi = {
      source  = "azure/azapi"         # Provider source
      version = ">= 2.0.0"            # Provider version constraint
    }

    null = {
      source  = "hashicorp/null"      # Provider source
      version = "~> 3.2"              # Provider version constraint
    }
  }
}

provider "azurerm" {
  features {} # Enable all default features for azurerm

 
}

provider "azapi" {

  # No additional configuration required for azapi provider

}


