import datetime
import os
from threading import Timer

from humanize import filesize as hf


viewable_formats = {
    "avi", "mp4", "mkv", "wmv",
    "mkv", "webm", "mov",

    "tif", "tiff", "bmp", "jpg",
    "jpeg", "gif", "png",

    "pdf",

    "txt"
}


emojis = {
    "avi": "🎞️", "mp4": "🎞️",
    "wmv": "🎞️", "mkv": "🎞️",
    "webm": "🎞️", "mov": "🎞️",

    "tif": "🖼️", "tiff": "🖼️",
    "bmp": "🖼️", "jpg": "🖼️",
    "jpeg": "🖼️", "gif": "🖼️",
    "png": "🖼️", "raw": "🖼️",
    
    "srt": "ℹ️", "sbv": "ℹ️",
    
    "pdf": "📕",

    "txt": "📝"
}


class Session:
    def __init__(self, expire, token):
        self.expire = expire
        self.token = token


def autodelete_sessions(sessions):
    Timer(1800, autodelete_sessions, args=(sessions,)).start()

    now = datetime.datetime.now()

    for i, session in enumerate(sessions):
        if session.expire <= now:
            del sessions[i]


def session_is_valid(token, sessions):
    if not token: return False

    for session in sessions:
        if session.token == token: return True

    return False


def get_dir_content(d):
    dir_content = os.listdir(d)
    folders = [item + '/' for item in dir_content if not os.path.isfile(d + "/" + item)]
    files = [(item, hf.naturalsize(os.path.getsize(d + "/" + item))) for item in dir_content if os.path.isfile(d + "/" + item)]
    return files, folders


def emoji_selector(filename):
    print(filename)
    _, extension = os.path.splitext(filename)

    # Removing leading dot
    extension = extension[1:]

    return emojis.get(extension.lower(), "📄")
