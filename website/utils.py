import datetime
import difflib
import os
from pathlib import Path
from threading import Timer


from humanize import filesize as hf


viewable_formats = {
    "avi", "mp4", "mkv", "wmv",
    "m4v", "webm", "mov", "mpg",

    "tif", "tiff", "bmp", "jpg",
    "jpeg", "gif", "png",

    "wav", "mp3", "wma", "ogg",
    "pcm", "aiff", "aac", "flac",

    "pdf",

    "txt"
}


emojis = {
    "avi": "🎞️", "mp4": "🎞️",
    "wmv": "🎞️", "mkv": "🎞️",
    "webm": "🎞️", "mov": "🎞️",
    "mpg": "🎞️","m4v": "🎞️",

    "tif": "🖼️", "tiff": "🖼️",
    "bmp": "🖼️", "jpg": "🖼️",
    "jpeg": "🖼️", "gif": "🖼️",
    "png": "🖼️", "raw": "🖼️",

    "srt": "ℹ️", "sbv": "ℹ️",

    "wav": "🎵", "mp3": "🎵",
    "wma": "🎵", "ogg": "🎵",
    "pcm": "🎵", "aiff": "🎵",
    "aac": "🎵", "flac": "🎵",

    "zip": "🗃", "rar": "🗃",
    "7z": "🗃", "gz": "🗃",

    "pdf": "📕",

    "txt": "📝"
}


class Session:
    def __init__(self, expire, token):
        self.expire = expire
        self.token = token


class BetterFile(dict):
    def __init__(self, *args):
        self.update(*args)
        self.__dict__.update(*args)

        self.name : str
        self.size : str
        self.path : str


def autodelete_sessions(sessions: list[Session]):
    Timer(1800, autodelete_sessions, args=(sessions,)).start()

    now = datetime.datetime.now()

    for i, session in enumerate(sessions):
        if session.expire <= now:
            del sessions[i]


def session_is_valid(token: str, sessions: list[Session]) -> bool:
    if not token: return False

    for session in sessions:
        if session.token == token: return True

    return False


def get_dir_content(d: str) -> tuple[list[BetterFile], list[str]]:
    dir_content = os.listdir(d)
    folders = [item + '/' for item in dir_content if not os.path.isfile(d + "/" + item)]
    files = [
        BetterFile({ "name": item, "size": hf.naturalsize(os.path.getsize(d + "/" + item)) })
        for item in dir_content
        if os.path.isfile(d + "/" + item)
    ]

    return files, folders


def emoji_selector(filename: str) -> str:
    _, extension = os.path.splitext(filename)

    # Removing leading dot
    extension = extension[1:]

    return emojis.get(extension.lower(), '📄')


def search_filename(d: str, name: str) -> list[BetterFile]:
    dir_content = os.listdir(d)

    folders = [item + '/' for item in dir_content if not os.path.isfile(os.path.join(d, item))]

    files = []
    for item in dir_content:
        item_name = Path(item).stem.lower().replace('_', ' ')
        if os.path.isfile(d + item) and (name in item_name or difflib.SequenceMatcher(a=name, b=item_name).ratio() >= 0.80):
            item_size = hf.naturalsize(os.path.getsize(d + item))
            item_path = os.path.join(d.replace(os.environ.get('BASE_DIR'), ''), item)
            files.append(BetterFile({ "path": item_path, "name": item, "size": item_size }))

    return files + sum([search_filename(d + folder, name) for folder in folders], start=[])
