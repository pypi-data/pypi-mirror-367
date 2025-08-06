import json
from dataclasses import asdict, dataclass, field
from datetime import datetime


@dataclass
class Session:
    """
    Represents a user session in the Vecna CLI.

    Attributes:
        unlocked (bool): Indicates if the session is currently unlocked.
        timestamp (str): ISO formatted timestamp of when the session was created or last modified.
    """

    unlocked: bool = field(
        default=True,
        metadata={"description": "Indicates if the session is currently unlocked."},
    )
    timestamp: str = field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        metadata={
            "description": (
                "ISO formatted timestamp of when the session was created or last modified."
            )
        },
    )


@dataclass
class BaseModel:
    """
    Base class for all models in the Vecna CLI.
    Provides a common interface for dumping model data as JSON or dictionary.
    """

    def model_dump_json(self, indent: int = 2) -> str:
        """
        Dumps the model as a JSON string with indentation.

        Args:
            indent (int): The number of spaces to use for indentation.

        Returns:
            str: The JSON representation of the model.
        """
        return json.dumps(asdict(self), indent=indent)

    def model_dump(self) -> dict:
        """
        Dumps the model as a dictionary.

        Returns:
            dict: The dictionary representation of the model.
        """
        return asdict(self)


@dataclass
class Credential(BaseModel):
    """
    Represents a credential stored in the Vecna CLI vault.

    Attributes:
        name (str): The name of the credential.
        username (str): The username associated with the credential.
        password (str): The password associated with the credential.
        notes (Optional[str]): Optional notes associated with the credential.
        tags (Optional[List[str]]): Optional tags associated with the credential.
    """

    name: str = field(metadata={"description": "The name of the credential."})
    username: str = field(metadata={"description": "The username associated with the credential."})
    password: str = field(metadata={"description": "The password associated with the credential."})
    notes: str | None = field(
        default="",
        metadata={"description": "Optional notes associated with the credential."},
    )
    tags: list[str] | None = field(
        default=None,
        metadata={"description": "Optional tags associated with the credential."},
    )


@dataclass
class UpdateCredential(Credential):
    """
    Represents an update operation for a credential in the Vecna CLI vault.
    Inherits from Credential and allows for updating specific fields.

    Attributes:
        new_name (Optional[str]): New name for the credential, if being updated.
        username (Optional[str]): New username for the credential, if being updated.
        password (Optional[str]): New password for the credential, if being updated.
        notes (Optional[str]): New notes for the credential, if being updated.
        tags (Optional[List[str]]): New tags for the credential, if being updated.
    """

    new_name: str | None = field(
        default=None,
        metadata={"description": "New name for the credential, if being updated."},
    )
    username: str | None = field(
        default=None,
        metadata={"description": "New username for the credential, if being updated."},
    )
    password: str | None = field(
        default=None,
        metadata={"description": "New password for the credential, if being updated."},
    )


@dataclass
class Alias(BaseModel):
    """
    Represents an alias in the Vecna CLI vault.

    Attributes:
        name (str): The name of the alias.
        command (str): The command associated with the alias.
        notes (Optional[str]): Optional notes associated with the alias.
        tags (Optional[List[str]]): Optional tags associated with the alias.
    """

    name: str = field(metadata={"description": "The name of the alias."})
    command: str = field(metadata={"description": "The command associated with the alias."})
    notes: str | None = field(
        default="",
        metadata={"description": "Optional notes associated with the alias."},
    )
    tags: list[str] | None = field(
        default=None,
        metadata={"description": "Optional tags associated with the alias."},
    )


@dataclass
class UpdateAlias(Alias):
    """
    Represents an update operation for an alias in the Vecna CLI vault.
    Inherits from Alias and allows for updating specific fields.

    Attributes:
        new_name (Optional[str]): New name for the alias, if being updated.
        command (Optional[str]): New command for the alias, if being updated.
        notes (Optional[str]): New notes for the alias, if being updated.
        tags (Optional[List[str]]): New tags for the alias, if being updated.
    """

    new_name: str | None = field(
        default=None,
        metadata={"description": "New name for the alias, if being updated."},
    )
    command: str | None = field(
        default=None,
        metadata={"description": "New command for the alias, if being updated."},
    )


@dataclass
class VaultData(BaseModel):
    """
    Represents the data structure of the Vecna CLI vault.
    Attributes:
        aliases (dict[str, Alias]): A dictionary of aliases stored in the vault.
        credentials (dict[str, Credential]): A dictionary of credentials stored in the vault.
    """

    credentials: dict[str, Credential] = field(
        default_factory=dict, metadata={"description": "The decrypted credential data."}
    )
    aliases: dict[str, Alias] = field(
        default_factory=dict, metadata={"description": "The decrypted alias data."}
    )
