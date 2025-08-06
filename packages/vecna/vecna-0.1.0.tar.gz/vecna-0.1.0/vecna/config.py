from importlib.metadata import PackageNotFoundError, version
from pathlib import Path


def get_version() -> str:
    """Return the installed version of the Vecna CLI package."""
    try:
        return version("vecna")
    except PackageNotFoundError:
        return "unknown"


CLI_VERSION = get_version()

# -----------------------------
# File & Directory Paths
# -----------------------------
VECNA_DIR = Path.home() / ".vecna"

# Vault file (encrypted secrets)
VAULT_FILE = VECNA_DIR / "vault.enc"

# Session tracking
SESSION_FILE = VECNA_DIR / "session.json"
SESSION_LIFESPAN = 60 * 30  # 30 minutes

# Config file
CONFIG_FILE = VECNA_DIR / "config.json"

# -----------------------------
# Encryption Settings
# -----------------------------
KEY_DERIVATION_ITERATIONS = 200_000  # Used in PBKDF2 or Argon2
KEY_LENGTH = 32  # 256 bits (32 bytes) for AES
KEY_ENCRYPTION_ALGORITHM = "AES-GCM"

# In-memory key caching (Linux-specific)
KEY_CACHE_DIR = Path("/dev/shm")
KEY_CACHE_FILE = KEY_CACHE_DIR / "key.cache"
