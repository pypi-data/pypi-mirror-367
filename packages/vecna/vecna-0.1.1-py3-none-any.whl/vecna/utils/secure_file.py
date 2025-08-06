import os


def read_secure_file(
    file_path: str,
) -> bytes | None:
    """
    Reads a file securely by setting appropriate permissions.

    Args:
        file_path (str): The path to the file to read.

    Returns:
        bytes: The contents of the file or None if the file does not exist.
    """
    if not os.path.exists(file_path):
        return None

    os.chmod(file_path, 0o600)
    with open(file_path, "rb") as f:
        data = f.read()

    os.chmod(file_path, 0o400)
    return data


def write_secure_file(
    file_path: str,
    data: bytes,
):
    """
    Writes data to a file securely by setting appropriate permissions.

    Args:
        file_path (str): The path to the file to write.
        data (bytes): The data to write to the file.

    Raises:
        IOError: If there is an error writing to the file.
    """
    if os.path.exists(file_path):
        os.chmod(file_path, 0o600)

    with open(file_path, "wb") as f:
        f.write(data)

    os.chmod(file_path, 0o400)


def delete_secure_file(
    file_path: str,
):
    """
    Deletes a file securely by setting appropriate permissions before deletion.

    Args:
        file_path (str): The path to the file to delete.

    Raises:
        IOError: If there is an error deleting the file.
    """
    if not os.path.exists(file_path):
        return

    os.chmod(file_path, 0o600)
    os.remove(file_path)
