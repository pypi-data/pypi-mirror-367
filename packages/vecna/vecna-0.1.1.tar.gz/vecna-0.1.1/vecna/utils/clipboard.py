def copy_to_clipboard(
    text: str,
) -> bool:
    """
    Copies the given text to the system clipboard.

    Args:
        text (str): The text to copy to the clipboard.

    Returns:
        bool: True if the text was successfully copied, False otherwise.
    """
    try:
        import pyperclip

        pyperclip.copy(text)
        return True
    except Exception:
        return False
