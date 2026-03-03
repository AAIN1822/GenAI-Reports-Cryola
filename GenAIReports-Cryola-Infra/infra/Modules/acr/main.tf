resource "azurerm_container_registry" "fsdu_acr" {
  name                             = var.acr_name                      # Name of the ACR instance
  resource_group_name              = var.resourcegroupname              # Resource group where ACR will be created
  location                         = var.location                      # Azure region for the ACR
  sku                              = "Premium"                        # SKU tier for ACR (Premium for advanced features)
  admin_enabled                    = false                             # Whether admin user is enabled (false for security)
  zone_redundancy_enabled          = true                              # Enable zone redundancy for high availability
  public_network_access_enabled    = var.public_network_access_enabled  # Allow or block public network access
  tags                             = var.tags                          # Tags for resource organization
}

resource "null_resource" "import_nginx" {

  provisioner "local-exec" {
    command     = <<EOT
      $tagExists = az acr repository show-tags --name ${azurerm_container_registry.fsdu_acr.name} --repository nginx --query "[?@=='latest']" -o tsv
      if (-not $tagExists) {
        az acr import --name ${azurerm_container_registry.fsdu_acr.name} --source docker.io/library/nginx:latest --image nginx:latest
      } else {
        Write-Host "nginx:latest already exists in ACR, skipping import."
      }
    EOT
    interpreter = ["PowerShell", "-Command"] # Use PowerShell for command execution
  }
  triggers = {
    acr_id        = azurerm_container_registry.fsdu_acr.id # Trigger on ACR resource ID change
    force_reimport = timestamp()                           # Force re-import on every apply (timestamp always changes)
  }

  # Azure Container Registry (ACR) Module
  # This module provisions an Azure Container Registry and related resources for secure container image management and monitoring.

  # Creates an Azure Container Registry (ACR) for storing and managing container images.
  # Premium SKU is used for advanced features like zone redundancy and enhanced security.
  depends_on = [azurerm_container_registry.fsdu_acr]
}

# Monitor diagnostics
resource "azurerm_monitor_diagnostic_setting" "acr_diagnostics" {
  name                       = "acr-diagnostics"                        # Name of the diagnostic setting
  target_resource_id         = azurerm_container_registry.fsdu_acr.id    # Resource ID of the ACR to monitor
  log_analytics_workspace_id = var.log_analytics_workspace_id            # Log Analytics workspace for diagnostics

  # --------------------
  # Logs
  # --------------------
  enabled_log {
    category = "ContainerRegistryLoginEvents"         # Capture login events to the registry
  }

  enabled_log {
    category = "ContainerRegistryRepositoryEvents"    # Capture repository events (push/pull/delete)
  }

  # --------------------
  # Metrics
  # --------------------
  metric {
    category = "AllMetrics"   # Collect all available metrics
    enabled  = true           # Enable metrics collection
  }

  depends_on = [
    azurerm_container_registry.fsdu_acr                # Ensure ACR is created before diagnostics
  ]
}
