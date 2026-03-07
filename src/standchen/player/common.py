from pathlib import Path

from django.conf import settings


VALID_EXTENSIONS = [".mp3", ".wav", ".ogg", ".flac"]


def get_files_and_directories(path: str) -> tuple[list[str], list[str]]:
    """
    Return all files and directories under a provided directory
    """
    fps, dirs = [], []
    for obj in Path(path).glob("**/*"):
        if obj.is_file() and obj.suffix in VALID_EXTENSIONS:
            fps.append(obj)
        if obj.is_dir():
            dirs.append(obj)

    return fps, dirs


def get_permitted_filepaths() -> tuple[list[str], list[str]]:
    """
    Return a list of all local files/directories under directories in settings.permitted_filepaths
    """
    permitted_dirs: list[str] = settings.SETTINGS_FILE["permitted_filepaths"]
    filepaths = set()
    directories = set()
    for fp in permitted_dirs:
        new_fps, new_dirs = get_files_and_directories(fp)
        filepaths |= set(new_fps)
        directories |= set(new_dirs)

    return sorted(list(filepaths)), sorted(list(directories))
