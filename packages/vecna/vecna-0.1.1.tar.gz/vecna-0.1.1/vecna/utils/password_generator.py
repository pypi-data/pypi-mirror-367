import random
import string


def generate_password(
    length: int = 15,
    use_numbers: bool = True,
    use_special_chars: bool = True,
) -> str:
    """
    Generates a secure random password.

    Args:
        length (int): Length of the password to generate. Default is 15.
        use_numbers (bool): Whether to include numbers in the password. Default is True.
        use_special_chars (bool): Whether to include special characters in the password.
        Default is True.

    Returns:
        str: A randomly generated password.
    """
    characters = string.ascii_letters
    if use_numbers:
        characters += string.digits
    if use_special_chars:
        characters += string.punctuation

    return "".join(random.choice(characters) for _ in range(length))
