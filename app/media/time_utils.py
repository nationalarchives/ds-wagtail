def parse_chapter_time_to_seconds(raw_value):
    if raw_value is None:
        return 0
    if isinstance(raw_value, int):
        return max(raw_value, 0)
    if isinstance(raw_value, str):
        value = raw_value.strip()
        if value.isdigit():
            return int(value)
        if ":" in value:
            parts = value.split(":")
            try:
                if len(parts) == 2:
                    minutes, seconds = map(int, parts)
                    return max(minutes, 0) * 60 + max(seconds, 0)
                if len(parts) == 3:
                    hours, minutes, seconds = map(int, parts)
                    return (
                        max(hours, 0) * 3600
                        + max(minutes, 0) * 60
                        + max(seconds, 0)
                    )
            except ValueError:
                return 0
    return 0


def format_seconds_mmss(total_seconds):
    minutes, seconds = divmod(max(int(total_seconds or 0), 0), 60)
    return f"{minutes:02d}:{seconds:02d}"
