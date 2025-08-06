import json
import os
from typing import Self

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from ..config import (
    KEY_CACHE_FILE,
    KEY_DERIVATION_ITERATIONS,
    KEY_LENGTH,
    VAULT_FILE,
    VECNA_DIR,
)
from ..models import Alias, Credential, UpdateAlias, UpdateCredential, VaultData
from ..utils import delete_secure_file, read_secure_file, write_secure_file


class Vault:
    def __init__(self):
        self.salt: bytes | None = None
        self.nonce: bytes | None = None
        self.encrypted_data: bytes | None = None
        self.data: VaultData = VaultData()

    @staticmethod
    def _delete_key():
        """
        Delete the cached encryption key.

        Returns:
            None
        """
        delete_secure_file(KEY_CACHE_FILE)

    @staticmethod
    def _load_key() -> bytes | None:
        """
        Retrieve the cached encryption key.

        Returns:
            bytes | None: The cached encryption key if it exists, otherwise None
        """
        key = read_secure_file(KEY_CACHE_FILE)
        return key if key else None

    @staticmethod
    def _save_key(key: bytes):
        """
        Cache the derived encryption key securely.

        Args:
            key (bytes): The derived encryption key
        """
        write_secure_file(KEY_CACHE_FILE, key)

    @staticmethod
    def _generate_salt() -> bytes:
        """
        Generate a cryptographically secure random salt.

        Returns:
            bytes: A 16-byte cryptographically secure random salt
        """
        return os.urandom(16)

    @staticmethod
    def _generate_nonce() -> bytes:
        """
        Generate a cryptographically secure random nonce.

        Returns:
            bytes: A 12-byte cryptographically secure random nonce
        """
        return os.urandom(12)

    def _decrypt_data(self, key: bytes):
        """
        Decrypt the encrypted vault data using AES-GCM and the derived encryption key.

        Args:
            key (bytes): The derived encryption key

        Returns:
            None
        """
        self.data = VaultData(
            **json.loads(AESGCM(key).decrypt(self.nonce, self.encrypted_data, None).decode())
        )
        for data_type, data_values in self.data.model_dump().items():
            if data_type == "credentials":
                self.data.credentials = {
                    cred_name: Credential(**cred) for cred_name, cred in data_values.items()
                }
            elif data_type == "aliases":
                self.data.aliases = {
                    alias_name: Alias(**alias) for alias_name, alias in data_values.items()
                }

    def _derive_key(self, password: str) -> bytes:
        """
        Derives an encryption key the password using PBKDF2.

        Args:
            password (str): The password to derive the encryption key from

        Returns:
            bytes: The derived key of length KEY_LENGTH bytes
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=KEY_LENGTH,
            salt=self.salt,
            iterations=KEY_DERIVATION_ITERATIONS,
            backend=default_backend(),
        )
        return kdf.derive(password.encode())

    def _encrypt_data(self, key: bytes):
        """
        Encrypt the current vault data using AES-GCM and the derived encryption key.

        Args:
            key (bytes): The derived encryption key

        Returns:
            None
        """
        self.encrypted_data = AESGCM(key).encrypt(
            self.nonce, self.data.model_dump_json().encode(), None
        )

    def _key_is_valid(self, key: bytes) -> bool:
        """
        Validate whether the provided encryption key correctly decrypts the vault.

        Args:
            key (bytes): The derived encryption key

        Returns:
            bool: True if the key is valid, False otherwise
        """
        try:
            AESGCM(key).decrypt(self.nonce, self.encrypted_data, None)
            return True
        except Exception:
            return False

    def _store_vault_to_disk(self):
        """
        Persist the current encrypted vault state to disk.

        Returns:
            None
        """
        write_secure_file(
            VAULT_FILE,
            self.salt + self.nonce + self.encrypted_data,
        )

    def create(self, password: str) -> Self:
        """
        Create and initialize a new encrypted vault using the provided password.

        Args:
            password (str): The password to derive the encryption key from

        Returns:
            Self: The Vault instance (for chaining or reuse).

        Side Effects:
            - Creates the Vecna directory if it does not exist
            - Overwrites the existing vault
        """
        VECNA_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )
        self.salt = self._generate_salt()
        self.nonce = self._generate_nonce()
        key = self._derive_key(password)
        self._encrypt_data(key)
        self._store_vault_to_disk()
        return self

    def load(self, raise_no_key: bool = True) -> Self:
        """
        Load vault metadata (salt, nonce, encrypted data) from disk and decrypt if
        a cached key is available.

        If no key is found and `raise_no_key` is True, a ValueError is raised.

        Args:
            raise_no_key (bool): Whether to raise an exception if no cached key
            is found (default: True)

        Returns:
            Self: The Vault instance (for chaining or reuse).

        Raises:
            ValueError: If no cached key is found and raise_no_key is True
            FileNotFoundError: If the vault file does not exist
        """
        vault_file_data = read_secure_file(VAULT_FILE)
        self.salt = vault_file_data[:16]
        self.nonce = vault_file_data[16:28]
        self.encrypted_data = vault_file_data[28:]
        key = self._load_key()

        if key is None:
            if raise_no_key:
                raise ValueError("Please unlock the vault first.")
            return self

        self._decrypt_data(key)
        return self

    def lock(self) -> Self:
        """
        Locks the vault by removing the cached key.

        Returns:
            Self: The Vault instance (for chaining or reuse).
        """
        self._delete_key()
        return self

    def unlock(self, password: str) -> Self:
        """
        Unlock the vault by deriving and caching the encryption key.

        Args:
            password (str): The password to derive the encryption key from

        Returns:
            Self: The Vault instance (for chaining or reuse).

        Raises:
            ValueError: If the password is incorrect or vault decryption fails
        """
        key = self._derive_key(password)
        if not self._key_is_valid(key):
            raise ValueError("Invalid password.")
        self._save_key(key)
        return self

    def add_credential(self, credential: Credential):
        """
        Add a new credential to the decrypted vault and persist the change.

        Args:
            credential (Credential): The credential object to add

        Returns:
            None

        Raises:
            KeyError: If a credential with the same name already exists
        """
        if credential.name in self.data.credentials:
            raise KeyError(f"Credential '{credential.name}' already exists.")

        self.data.credentials[credential.name] = credential
        key = self._load_key()
        self._encrypt_data(key)
        self._store_vault_to_disk()

    def get_credential(self, name: str) -> Credential | None:
        """
        Retrieves a credential object from the vault by its name.

        Args:
            name (str): The name of the credential to retrieve.

        Returns:
        Credential | None: The credential if found, otherwise None.
        """
        if name not in self.data.credentials:
            return None
        return self.data.credentials[name]

    def list_credentials(self) -> list[Credential]:
        """
        List all credentials stored in the vault.

        Returns:
            list[Credential]: A list of all Credential objects currently stored in the vault.
        """
        return list(self.data.credentials.values())

    def delete_credential(self, name: str):
        """
        Deletes a credential from the vault.

        Args:
            name (str): The name of the credential to delete.

        Raises:
            KeyError: If the credential with the specified name does not exist in the vault.
        """
        if name not in self.data.credentials:
            raise KeyError(f"Credential '{name}' does not exist.")
        del self.data.credentials[name]
        key = self._load_key()
        self._encrypt_data(key)
        self._store_vault_to_disk()

    def update_credential(self, credential: UpdateCredential):
        """
        Update an existing credential in the vault.

        Args:
            credential (Credential): The updated credential object

        Raises:
            KeyError: If the credential with the specified name does not exist in the vault.
        """

        if credential.name not in self.data.credentials:
            raise KeyError(f"Credential '{credential.name}' does not exist.")

        if credential.new_name is not None:
            self.data.credentials[credential.new_name] = self.data.credentials.pop(credential.name)
            credential.name = credential.new_name
            credential.new_name = None

        for (
            key,
            value,
        ) in credential.model_dump().items():
            if value is not None:
                setattr(self.data.credentials[credential.name], key, value)

        key = self._load_key()
        self._encrypt_data(key)
        self._store_vault_to_disk()

    def add_alias(self, alias: Alias):
        """
        Add a new alias to the vault.

        Args:
            alias (Alias): The alias object to add

        Returns:
            None

        Raises:
            KeyError: If an alias with the same name already exists
        """
        if alias.name in self.data.aliases:
            raise KeyError(f"Alias '{alias.name}' already exists.")

        self.data.aliases[alias.name] = alias
        key = self._load_key()
        self._encrypt_data(key)
        self._store_vault_to_disk()

    def get_alias(self, name: str) -> Alias | None:
        """
        Retrieves an alias object from the vault by its name.

        Args:
            name (str): The name of the alias to retrieve.

        Returns:
            Alias | None: The alias if found, otherwise None.
        """
        if name not in self.data.aliases:
            return None
        return self.data.aliases[name]

    def list_aliases(self) -> list[Alias]:
        """
        List all aliases stored in the vault.

        Returns:
            list[Alias]: A list of all Alias objects currently stored in the vault.
        """
        return list(self.data.aliases.values())

    def delete_alias(self, name: str):
        """
        Deletes an alias from the vault.

        Args:
            name (str): The name of the alias to delete.

        Raises:
            KeyError: If the alias with the specified name does not exist in the vault.
        """
        if name not in self.data.aliases:
            raise KeyError(f"Alias '{name}' does not exist.")
        del self.data.aliases[name]
        key = self._load_key()
        self._encrypt_data(key)
        self._store_vault_to_disk()

    def update_alias(self, alias: UpdateAlias):
        """
        Update an existing alias in the vault.

        Args:
            alias (UpdateAlias): The updated alias object

        Raises:
            KeyError: If the alias with the specified name does not exist in the vault.
        """

        if alias.name not in self.data.aliases:
            raise KeyError(f"Alias '{alias.name}' does not exist.")

        if alias.new_name is not None:
            self.data.aliases[alias.new_name] = self.data.aliases.pop(alias.name)
            alias.name = alias.new_name
            alias.new_name = None

        for (
            key,
            value,
        ) in alias.model_dump().items():
            if value is not None:
                setattr(self.data.aliases[alias.name], key, value)

        key = self._load_key()
        self._encrypt_data(key)
        self._store_vault_to_disk()

    def exists(self) -> bool:
        """
        Check if the vault file exists.

        Returns:
            bool: True if the vault file exists, False otherwise
        """
        try:
            vault = read_secure_file(VAULT_FILE)
        except FileNotFoundError:
            return False
        return vault is not None and len(vault) > 0
