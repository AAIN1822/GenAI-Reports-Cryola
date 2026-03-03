from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import os

KEYVAULT_NAME = os.environ["AZURE_KEYVAULT_NAME"]
KEYVAULT_URL = f"https://{KEYVAULT_NAME}.vault.azure.net/"

SECRET_MAP = {
    "COSMOS_KEY": "cosmos-key",
    "MICROSOFT_CLIENT_ID": "microsoft-client-id",
    "MICROSOFT_TENANT_ID": "microsoft-tenant-id",
    "AZURE_OPENAI_API_KEY": "azure-openai-api-key",
    "JWT_SECRET_KEY": "jwt-secret-key",
    "DAM_AUTH_KEY": "dam-auth-key",
}

def load_keyvault_secrets() -> None:
    credential = DefaultAzureCredential(
        exclude_interactive_browser_credential=True
    )
    client = SecretClient(
        vault_url=KEYVAULT_URL,
        credential=credential
    )
    for env_name, secret_name in SECRET_MAP.items():
        if not os.getenv(env_name):
            secret = client.get_secret(secret_name)
            os.environ[env_name] = secret.value
