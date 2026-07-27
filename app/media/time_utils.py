def parse_chapter_time_string_to_seconds(raw_value):
    if not isinstance(raw_value, str):
        return None

    value = raw_value.strip()
    parts = value.split(":")

    if len(parts) != 3 or any(not part.isdigit() for part in parts):
        return None

    hours, minutes, seconds = map(int, parts)
    if hours < 0 or not (0 <= minutes <= 59 and 0 <= seconds <= 59):
        return None

    return hours * 3600 + minutes * 60 + seconds


def parse_chapter_time_to_seconds(raw_value):
    if raw_value is None:
        return None

    if isinstance(raw_value, int):
        return raw_value if raw_value >= 0 else None

    if isinstance(raw_value, str):
        value = raw_value.strip()
        if value.isdigit():
            return int(value)

        return parse_chapter_time_string_to_seconds(value)

    return None


def format_seconds_hhmmss(total_seconds):
    total_seconds = max(int(total_seconds or 0), 0)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
