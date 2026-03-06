from pathlib import Path

from django.conf import settings


VALID_EXTENSIONS = [".mp3", ".wav", ".ogg", ".flac"]


def get_permitted_filepaths() -> list[str]:
    """
    Return a list of all local files under directories in settings.permitted_filepaths
    """
    directories: list[str] = settings.SETTINGS_FILE["permitted_filepaths"]
    filepaths = set()
    for fp in directories:
        new_files = [
            f
            for f in Path(fp).glob("**/*")
            if f.is_file() and f.suffix in VALID_EXTENSIONS
        ]
        filepaths |= set(new_files)

    return sorted(list(filepaths))
