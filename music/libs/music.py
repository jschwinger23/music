import os
from operator import itemgetter

from mutagen.mp3 import EasyMP3
from mutagen._tools.mid3v2 import write_files

from .qq_music import QQMusic


class Music:
    @classmethod
    def from_filename(cls, filename: str):
        return cls(os.path.abspath(filename))

    def __init__(self, filename):
        self.mp3 = EasyMP3(filename)

    def update_from_qqmusic(self, qq_music: QQMusic):
        artist, title = os.path.basename(self.mp3.filename).split('-')
        music_meta = qq_music.search(
            artist=artist.strip(), title=title.strip()[:-4])
        self.update_meta(music_meta)

    def update_meta(self, music_meta: dict):
        meta_attrs = ('artist', 'title', 'date', 'tracknumber', 'album')
        meta_vals = itemgetter(meta_attrs)(music_meta)
        self.mp3.update(zip(meta_attrs, meta_vals))
        self.mp3.save()

        write_files([('--APIC', music_meta['picture_filename'])],
                    [self.mp3.filename], False)
