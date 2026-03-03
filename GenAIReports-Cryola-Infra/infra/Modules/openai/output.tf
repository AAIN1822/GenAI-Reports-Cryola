output "aifoundry_raw_output" {
  description = "Raw output of the AI Foundry resource for debugging endpoint extraction."
  value       = azapi_resource.fsdu_aifoundry.output
}
output "aifoundry_endpoint" {
  value = azapi_resource.fsdu_aifoundry.output.properties.endpoint
}


output "openai_account_id" {
  description = "Resource ID of the AI Foundry account"
  value       = azapi_resource.fsdu_aifoundry.id
}

output "aifoundry_principal_id" {
  description = "System-assigned identity principal ID of the AI Foundry account"
  value       = try(azapi_resource.fsdu_aifoundry.output.identity.principalId, "")
}

output "aifoundry_primary_access_key" {
  description = "Primary access key for AI Foundry account"
  value       = try(azapi_resource_action.aifoundry_list_keys.output.key1, "")
  sensitive   = true
}

output "aifoundry_secondary_access_key" {
  description = "Secondary access key for AI Foundry account"
  value       = try(azapi_resource_action.aifoundry_list_keys.output.key2, "")
  sensitive   = true
}

output "aifoundry_name" {
  description = "Name of the AI Foundry account"
  value       = azapi_resource.fsdu_aifoundry.name
  
}

