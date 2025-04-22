import hvac
import os

class HVACClient:
    def __init__(self, url=None, token=None):
        self.url = url or os.environ.get("VAULT_ADDR")
        self.token = token or os.environ.get("VAULT_TOKEN")
        self._initialize_client()

    def _initialize_client(self):
        if not self.url:
            raise ValueError("Vault URL (VAULT_ADDR) is not set.")
        if not self.token:
            raise ValueError("Vault token (VAULT_TOKEN) is not set.")

        try:
            self.client = hvac.Client(url=self.url, token=self.token)
            self.client.is_authenticated()
        except hvac.exceptions.VaultError as e:
            raise ValueError(f"Failed to initialize Vault client: {e}")

    def read(self, path):
        if not self.client:
            raise ValueError("Vault client is not initialized.")

        try:
            response = self.client.read(path)
            if response and response.get("data"):
              return response["data"]["data"]
            else:
              return None
        except hvac.exceptions.InvalidPath:
            return None #Return None for non-existent path.
        except hvac.exceptions.VaultError as e:
            raise ValueError(f"Failed to read from Vault path {path}: {e}")

    def write(self, path, data):
        return self.client.secrets.kv.v2.create_or_update_secret(path, secret=data)

    def delete(self, path):
        if not self.client:
            raise ValueError("Vault client is not initialized.")

        try:
            response = self.client.delete(path)
            return response
        except hvac.exceptions.VaultError as e:
            raise ValueError(f"Failed to delete from Vault path {path}: {e}")

    def list_secrets(self, path):

        if not self.client:
            raise ValueError("Vault client is not initialized.")

        try:
            response = self.client.list(path)
            if response and response.get('data') and response['data'].get('keys'):
              return response['data']['keys']
            else:
              return None
        except hvac.exceptions.InvalidPath:
          return None
        except hvac.exceptions.VaultError as e:
            raise ValueError(f"Failed to list keys at Vault path {path}: {e}")

    def is_authenticated(self):

      if self.client:
        return self.client.is_authenticated()
      return False