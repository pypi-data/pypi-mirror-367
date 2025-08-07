import functools
import json
import logging
import os
from pathlib import Path
import sys
import webbrowser
from urllib.parse import urlparse, parse_qs

from . import LOG_DIR
from .db import DBConfig

LOG_FILE = os.path.join(LOG_DIR, 'launcher.log')

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.handlers.TimedRotatingFileHandler(LOG_FILE, when='midnight')
handler.setFormatter(logging.Formatter('%(asctime)-15s %(levelname)-8s %(name)s: %(message)s'))
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)


def main():
    url = sys.argv[1]
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    logger.debug("parsed=%r query=%r", parsed, query)
    if parsed.netloc == 'launch':
        try:
            return launch(parsed, query)
        except Exception:
            logger.exception("Exception in launch.")
    else:
        logger.error("Don't know how to open %r", parsed.netloc)


LAUNCHERS = {}


def launcher(path):
    def inner(f):
        LAUNCHERS[path] = f

        @functools.wraps(f)
        def _launcher(*args, **kwargs):
            return f(*args, **kwargs)
        return _launcher
    return inner


def launch(parsed, query):
    logger.debug("launch called with parsed=%r", parsed)
    if parsed.path in LAUNCHERS:
        return LAUNCHERS[parsed.path](parsed, query)
    else:
        logger.error("Don't know how to launch %r", parsed)


@launcher('/steam')
def launch_steam(parsed, query):
    logger.debug("launch_steam called with parsed=%r", parsed)
    app_id = query.get('app_id')[0]
    webbrowser.open('steam://rungameid/{}'.format(app_id))


@launcher('/retroarch')
def launch_retroarch(parsed, query):
    logger.debug("launch_retroarch called with parsed=%r", parsed)

    RETROARCH_PATH = Path(DBConfig.get('GamestProtocolPlugin', 'retroarch_path', fallback='retroarch'))
    CONFIG_PATH = Path(DBConfig.get('GamestProtocolPlugin', 'config_path', fallback=os.path.expanduser('~/.config/retroarch')))
    PLAYLIST_PATH = CONFIG_PATH / 'playlists'

    rom_hash = query.get('hash')[0]
    playlists = [CONFIG_PATH/'content_favorites.lpl',
                 CONFIG_PATH/'content_history.lpl']
    playlists.extend(PLAYLIST_PATH.glob('*.lpl'))
    for pl in playlists:
        if not pl.exists():
            continue
        with open(pl, 'r') as f:
            data = json.load(f)
            items = data.get('items', [])
            for i in items:
                if i.get('crc32') == rom_hash:
                    path = i.get('path')
                    core = i.get('core_path')
                    if core == 'DETECT':
                        if data.get('default_core_path'):
                            logger.debug("Launching with default core %r",
                                         data.get('default_core_path'))
                            core = data.get('default_core_path')
                        else:
                            raise RuntimeError(
                                "No core set for {!r} (from {!r}).".format(i, parsed))
                    logger.debug("launching %r core=%r path=%r", RETROARCH_PATH, core, path)
                    os.execlp(RETROARCH_PATH, 'retroarch', '-L', core, path)
    else:
        logger.info("No matching content found: %r", rom_hash)


    webbrowser.open('steam://rungameid/{}'.format(app_id))
