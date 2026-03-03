# ============================================
# Container App Environment
# ============================================
# Managed infrastructure for running container apps with built-in networking
resource "azurerm_container_app_environment" "fsdu_con_env" {
  name                           = var.container_environment_name
  location                       = var.location
  resource_group_name            = var.resourcegroupname
  infrastructure_subnet_id       = var.subnet_id  # Deploy into private backend subnet
  internal_load_balancer_enabled = var.internal_load_balancer_enabled  # Internal only when private
}




# Pre-created user-assigned identity
resource "azurerm_user_assigned_identity" "acr_identity" {
  name                = "acr-identity"
  resource_group_name = var.resourcegroupname
  location            = var.location
}

# Assign AcrPull role to the identity
resource "azurerm_role_assignment" "acr_pull" {
  scope                = var.acr_id
  role_definition_name = "AcrPull"
  principal_id         = azurerm_user_assigned_identity.acr_identity.principal_id
  depends_on = [ azurerm_user_assigned_identity.acr_identity ]
}


# ============================================
# Container App Instance
# ============================================
# Serverless container deployment with auto-scaling and revision management
resource "azurerm_container_app" "fsdu_con_app" {
  name                         = var.container_app_name
  container_app_environment_id = azurerm_container_app_environment.fsdu_con_env.id
  resource_group_name          = var.resourcegroupname
  revision_mode                = "Single"
  depends_on = [ azurerm_role_assignment.acr_pull ]

  identity {
    type         = "SystemAssigned, UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.acr_identity.id]
  }

  registry {
    server   = var.acr_login_server
    identity = azurerm_user_assigned_identity.acr_identity.id
  }


  ingress {
    external_enabled           = !var.internal_load_balancer_enabled
    target_port                = 80
    allow_insecure_connections = false
    transport                  = "auto"

    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }

  template {
    revision_suffix = var.image_revision_suffix

    container {
      name   = var.container_name
      image  = var.container_image
      cpu    = var.cpu
      memory = var.memory

      env {
        name  = "APPLICATIONINSIGHTS_CONNECTION_STRING"
        value = var.appinsights_connection_string
      }
      # Pass the APIM gateway URL as the OpenAI endpoint
      env {
        name  = "OPENAI_API_URL"
        value = var.apim_gateway_url   # <-- APIM URL wired here
      }
    }

    min_replicas = 1
    max_replicas = 5
  }

  lifecycle {
    ignore_changes = [
      template[0].container[0].image
    ]
  }

  tags = var.tags
}


# ============================================
# RBAC Role Assignments for Container App
# ============================================
# Grant Container App identity permissions to access Azure services

# Allow Container App to access Storage Blob data
resource "azurerm_role_assignment" "storage_blob" {
  scope                = var.storage_account_id
  role_definition_name = "Storage Blob Data Contributor"  # Read/Write blob data
  principal_id         = azurerm_container_app.fsdu_con_app.identity[0].principal_id
}

# Allow Container App to query Cosmos DB
resource "azurerm_role_assignment" "cosmos_db" {
  scope                = var.cosmos_id
  role_definition_name = "Cosmos DB Account Reader Role"  # Read-only database access
  principal_id         = azurerm_container_app.fsdu_con_app.identity[0].principal_id
}

# Allow Container App to call OpenAI APIs
resource "azurerm_role_assignment" "openai" {
  scope                = var.ai_foundry_id
  role_definition_name = "Contributor"  # Full access to AI Foundry
  principal_id         = azurerm_container_app.fsdu_con_app.identity[0].principal_id
}



