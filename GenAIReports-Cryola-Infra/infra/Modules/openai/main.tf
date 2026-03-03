############################################
# Data - Get current subscription context
############################################
# Retrieves current subscription ID and tenant information for resource creation
data "azurerm_client_config" "current" {}
  # Retrieves current subscription and tenant context

############################################
# AI Foundry Account - WEST US 3
############################################
# Azure AI Foundry is the unified platform for deploying and managing AI models
# Located in westus3 for optimal OpenAI model availability and performance
resource "azapi_resource" "fsdu_aifoundry" {
  type      = "Microsoft.CognitiveServices/accounts@2025-06-01" # Resource type for AI Foundry
  name      = "${var.aifoundryname}-wus3"                        # Name of the AI Foundry account (region suffix)
  parent_id = "/subscriptions/${data.azurerm_client_config.current.subscription_id}/resourceGroups/${var.resourcegroupname}" # Parent resource group
  location  = var.openai_location                                 # Region for GPT-5/O3 model access

  body = {
    kind = "AIServices"                                          # Account kind
    sku  = { name = "S0" }                                       # SKU tier (S0 = Standard)
    identity = { type = "SystemAssigned" }                       # Managed identity
    properties = {
      customSubDomainName     = "${var.aifoundryname}-wus3"      # Custom subdomain for API
      publicNetworkAccess     = var.public_network_access_enabled ? "Enabled" : "Disabled" # Public network access
      allowProjectManagement  = true                              # Enable project management
    }
    tags = var.tags                                               # Tags for resource organization
  }
  lifecycle {
    ignore_changes = [
      tags,                                                      # Ignore tag changes
      identity,                                                  # Ignore identity changes
      body["properties"],                                       # Ignore property changes
      body["sku"]                                               # Ignore SKU changes
    ]
  }

}

############################################
# List Keys Action - Fetch account access keys
############################################
# Uses azapi resource action to retrieve key1/key2 for the account
resource "azapi_resource_action" "aifoundry_list_keys" {
  type        = "Microsoft.CognitiveServices/accounts@2025-06-01" # Resource type for AI Foundry
  resource_id = azapi_resource.fsdu_aifoundry.id                  # Resource ID of AI Foundry
  action      = "listKeys"                                       # Action to list keys
  body        = {}                                               # Empty body for action
  response_export_values = ["*"]
  #response_export_values = ["key1", "key2"]                     # Keys to export
}

############################################
# Responsible AI (RAI) Policy - WEST US 3
############################################
# Content filtering and safety measures for AI model outputs
# Prevents generation of harmful, hateful, or inappropriate content
resource "azapi_resource" "rai_policy_westus3" {
  type      = "Microsoft.CognitiveServices/accounts/raiPolicies@2025-06-01"
  name      = "MerchDisplay-CustomFilter"
  parent_id = azapi_resource.fsdu_aifoundry.id

  body = {
    properties = {
      mode           = "Default"  # Standard content filtering mode
      basePolicyName = "Microsoft.DefaultV2"  # Microsoft's default safety policy
      contentFilters = var.content_filters_custom  # Custom filtering rules for specific use case
    }
  }
}

############################################
# GPT-5 Deployment - WEST US 3
############################################
# Advanced reasoning model for complex tasks, code generation, and analysis
# GlobalStandard SKU provides auto-scaling and pay-per-token pricing
resource "azapi_resource" "gpt5_deployment" {
  type      = "Microsoft.CognitiveServices/accounts/deployments@2025-06-01"
  name      = "gpt-5"
  parent_id = azapi_resource.fsdu_aifoundry.id

  body = {
    sku = {
      name     = "GlobalStandard"  # Auto-scaling SKU with reserved capacity
      capacity = var.gpt5_capacity  # Reserved TPM (Tokens Per Minute) for consistent performance
    }
    properties = {
      model = {
        format  = "OpenAI"  # OpenAI format deployment
        name    = "gpt-5"   # Latest GPT-5 model
        version = "2025-08-07"  # Model version release date
      }
      versionUpgradeOption = "OnceNewDefaultVersionAvailable"  # Auto-upgrade to new versions
      currentCapacity      = var.gpt5_capacity
      raiPolicyName        = "MerchDisplay-CustomFilter"  # Apply content filtering
    }
  }

  depends_on = [azapi_resource.rai_policy_westus3]  # Ensure RAI policy exists first
}

############################################
# O3 Deployment - WEST US 3
############################################
# Reasoning model optimized for deep thinking tasks and complex problem solving
# Best for multi-step reasoning and verification scenarios
resource "azapi_resource" "o3_deployment" {
  type      = "Microsoft.CognitiveServices/accounts/deployments@2025-06-01"
  name      = "o3"
  parent_id = azapi_resource.fsdu_aifoundry.id

  body = {
    sku = {
      name     = "GlobalStandard"  # Auto-scaling with reserved tokens
      capacity = var.o3_capacity   # Reserved TPM for O3 reasoning model
    }
    properties = {
      model = {
        format  = "OpenAI"
        name    = "o3"  # Reasoning-focused model
        version = "2025-04-16"
      }
      versionUpgradeOption = "OnceNewDefaultVersionAvailable"  # Keep model updated
      currentCapacity      = var.o3_capacity
      raiPolicyName        = "MerchDisplay-CustomFilter"
    }
  }

  depends_on = [
    azapi_resource.gpt5_deployment  # Deploy GPT-5 first to avoid throttling
  ]
}

############################################
# GPT-Image-1.5 Deployment - WEST US 3
############################################
# Image generation model for creating visual designs and artwork
# Specialized for merchandise design and creative asset generation
resource "azapi_resource" "gpt_image_1_5_deployment" {
  type      = "Microsoft.CognitiveServices/accounts/deployments@2025-06-01"
  name      = "gpt-image-1.5"
  parent_id = azapi_resource.fsdu_aifoundry.id

  body = {
    sku = {
      name     = "GlobalStandard"  # Auto-scaling image generation capacity
      capacity = var.gpt_image_1_5_capacity  # Reserved TPM for image API
    }
    properties = {
      model = {
        format  = "OpenAI"
        name    = "gpt-image-1.5"  # Latest image generation model
        version = "2025-12-16"  # Latest version with improved quality
      }
      versionUpgradeOption = "OnceNewDefaultVersionAvailable"
      currentCapacity      = var.gpt_image_1_5_capacity
      raiPolicyName        = "MerchDisplay-CustomFilter"  # Filter generated images for safety
    }
  }

  depends_on = [azapi_resource.o3_deployment]  # Sequential deployment to manage API quota
}

############################################
# OpenAI / AI Foundry Diagnostic Settings
############################################
resource "azurerm_monitor_diagnostic_setting" "openai_metrics" {
  name                       = "openai-metrics-only"
  target_resource_id         = azapi_resource.fsdu_aifoundry.id
  log_analytics_workspace_id = var.log_analytics_workspace_id

  metric {
    category = "AllMetrics"
    enabled  = true
  }

  depends_on = [
    azapi_resource.fsdu_aifoundry
  ]
}

