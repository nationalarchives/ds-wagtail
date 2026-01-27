def normalize_archive_letter(letter: str | None) -> str:
    """
    Normalize a letter for archive navigation and filtering.

    Args:
        letter: Single character or special value '0-9'

    Returns:
        - Lowercase letter (a-z) for alphabetic characters
        - '0-9' for the digits/symbols category
        - Empty string for invalid input
    """
    if not letter:
        return ""

    letter = letter.strip()

    if letter == "0-9":
        return "0-9"

    if len(letter) == 1 and letter.isalpha():
        return letter.lower()

    return ""
