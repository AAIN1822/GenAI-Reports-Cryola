variable "secrets" {
  description = "Map of secrets to store in Key Vault. Key is the secret name, value is the secret value"
  type        = map(string)
  default     = {}
}
variable "keyvault_id" {
  description = "The ID of the Key Vault where secrets will be stored"
  type        = string
}