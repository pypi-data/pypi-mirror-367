import datetime
import json

from ..config import SESSION_FILE, SESSION_LIFESPAN
from ..models import Session
from ..utils import delete_secure_file, read_secure_file, write_secure_file


def create_session():
    """
    Creates a session for the current user.

    This function creates a session file with a flag indicating that the user is authenticated
    and a timestamp of when the session was created. The file permissions are set to read-only
    after creation to prevent unauthorized modifications.

    Returns:
        None

    Side effects:
        - Creates or overwrites the session file defined by SESSION_FILE
        - Sets file permissions to 0o600 (read-write for owner only) before writing
        - Sets file permissions to 0o400 (read-only for owner) after writing
    """
    session_data = {
        "unlocked": True,
        "timestamp": datetime.datetime.now().isoformat(),
    }
    write_secure_file(
        SESSION_FILE,
        json.dumps(session_data).encode(),
    )


def end_session():
    """
    Ends the current session by removing the session file.

    This function attempts to securely delete the session file if it exists.
    It first changes the file permissions to 0o600 (read/write for owner only)
    before removing it from the filesystem.

    Returns:
        None: If the session file doesn't exist

    Note:
        This function relies on the SESSION_FILE constant being defined elsewhere
        in the module.
    """
    delete_secure_file(SESSION_FILE)


def is_session_active() -> bool:
    """
    Checks if there is an active session.

    This function checks for the existence of the session file and reads its contents
    to determine if the session is active (i.e., unlocked).

    Returns:
        bool: True if the session is active, False otherwise

    Raises:
        ValueError: If the session file does not exist
    """
    session_data = read_secure_file(SESSION_FILE)

    if session_data is None:
        return False

    try:
        session = Session(**json.loads(session_data.decode()))
    except Exception:
        return False

    if not session.unlocked:
        return False

    session_time = datetime.datetime.fromisoformat(session.timestamp)
    current_time = datetime.datetime.now()
    if (current_time - session_time).total_seconds() > SESSION_LIFESPAN:
        return False
    return True
