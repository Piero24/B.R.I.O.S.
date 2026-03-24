import os
from datetime import datetime, timedelta


def clean_old_logs(filepaths: list[str], days_to_keep: int = 30) -> None:
    """Scans the provided log files and removes any lines older than `days_to_keep`.

    This function parses the `[YYYY-MM-DD HH:MM:SS]` prefix at the start of each line.
    If a line lacks this prefix, it is preserved (to avoid accidentally deleting
    stack traces or malformed lines that belong to a recent event).

    Args:
        filepaths: A list of absolute or relative paths to log files.
        days_to_keep: The maximum age of a log line before it is discarded.
    """
    cutoff_date = datetime.now() - timedelta(days=days_to_keep)

    for filepath in filepaths:
        if not filepath or not os.path.exists(filepath):
            continue

        try:
            # Read all lines from the file
            with open(filepath, "r") as f:
                lines = f.readlines()

            retained_lines = []

            for line in lines:
                # Expected format: "[2026-03-10 15:00:24] ..."
                if not line.startswith("["):
                    retained_lines.append(line)
                    continue

                try:
                    # Extract the date string e.g. "2026-03-10"
                    date_str = line[1:11]
                    log_date = datetime.strptime(date_str, "%Y-%m-%d")

                    if log_date >= cutoff_date:
                        retained_lines.append(line)
                except ValueError:
                    # If parsing fails, hold onto the line just in case it's important
                    retained_lines.append(line)

            # Rewrite the file with only the retained lines
            with open(filepath, "w") as f:
                f.writelines(retained_lines)

        except (IOError, OSError):
            # Fail silently. It's just log cleanup; we don't want to crash the daemon.
            pass
