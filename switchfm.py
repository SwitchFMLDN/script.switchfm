import re
import time

import requests
import urllib.request

NOWPLAYING_URL  = ''
COVER_URL       = ''
LIVE_DJ         = 'https://switchfm.co.uk/api/kodi/addon.php?action=DJ'
AUDIO           = 'https://switchfm.co.uk/api/kodi/addon.php?action=stream'
VIDEO           = 'https://switchfm.co.uk/api/kodi/addon.php?action=video'
KEY_FILTER_RE = re.compile(r'[^\w\']+')

UPDATE_TIMEOUT = 2.0


LIVE_NOW     = requests.get(LIVE_DJ)
LIVE_STREAM  = requests.get(AUDIO)
VIDEO_STREAM = requests.get(VIDEO)



STREAMS = [
    {
        'channel': 0,
        'title': '[COLOR red]LIVE NOW:[/COLOR] [COLOR white][B]' + LIVE_NOW.text + '[/B][/COLOR]',
        'url_aac': LIVE_STREAM.text,
        'url_flac': LIVE_STREAM.text,
    },
    {
        'channel': 1,
        'title': 'Listen Live',
        'url_aac': LIVE_STREAM.text,
        'url_flac': LIVE_STREAM.text,
    },
    {
        'channel': 2,
        'title': 'Watch Live',
        'url_aac': VIDEO_STREAM.text,
        'url_flac': VIDEO_STREAM.text,
    },
]
STREAM_INFO = {s['url_aac']: s for s in STREAMS}
STREAM_INFO.update({s['url_flac']: s for s in STREAMS})


class NowPlaying():
    """Provides song information from the "nowplaying" API."""

    def __init__(self):
        """Constructor"""
        self.set_channel(None)

    def get_song_data(self, song_key):
        """Return a dict for the build_key()-created key, or None.

        The "cover" value will be an absolute URL.
        """
        return self.songs.get(song_key)

    def set_channel(self, channel):
        """Set the RP channel number, or None."""
        if channel is not None:
            self.url = NOWPLAYING_URL.format(channel)
        else:
            self.url = None
        self.current = None
        self.next_update = 0
        self.songs = {}

    def update(self):
        """Update song information from the API, if necessary.

        Calls the API only if the "refresh" timer has expired.

        Raises an exception on error responses or timeouts.
        """
        if self.url is None:
            return
        now = time.time()
        if now < self.next_update:
            return
        res = requests.get(self.url, timeout=UPDATE_TIMEOUT)
        res.raise_for_status()
        data = res.json()
        songs = {}
        for index, song in data['song'].items():
            if song['artist'] is None:
                song['artist'] = 'Unknown Artist'
            if song['title'] is None:
                song['title'] = 'Unknown Title'
            song['cover'] = COVER_URL.format(song['cover'])
            key = build_key((song['artist'], song['title']))
            songs[key] = song
            if index == '0':
                self.current = song
        self.songs = songs
        self.next_update = now + data['refresh']


def build_key(strings):
    """Return a normalized tuple of words in the strings."""
    result = []
    for s in strings:
        words = KEY_FILTER_RE.sub(' ', s).casefold().split()
        result.extend(words)
    return tuple(sorted(result))
