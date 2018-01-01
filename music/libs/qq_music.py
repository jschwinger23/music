import json
from pathlib import Path
from opertor import itemgetter
from typing import Optional

import requests


class Resource:
    @classmethod
    def from_file(cls, filename: str):
        with open(filename) as f:
            obj = json.load(f)
        meta, details = itemgetter('meta', 'details')(obj)
        return cls(meta, details)

    @classmethod
    def from_meta(cls, meta: dict):
        resp = requests.get(cls.URL_FORMATTER(meta=meta))
        resp.raise_for_status()
        details = resp.json()
        return cls(meta, details)

    def __init__(self, meta: dict, details: Optional[dict]=None):
        self.meta = meta
        self.details = details

    def to_json(self):
        return {
            'meta': self.meta,
            'details': self.details,
        }

    @property
    def name(self):
        pass


class AlbumCollection(Resource):
    def __iter__(self):
        for album_meta in self.details:
            album = Album.from_meta(album_meta)
            yield album


class Album(Resource):
    URL_FORMATTER = ''.format

    def __iter__(self):
        for song_meta in self.details:
            song = Song.from_meta(song_meta)
            yield song


class Song:
    URL_FORMATTER = ''.format


class QQMusicCache:
    def __init__(self, cid, uid):
        self.album_collection = AlbumCollection.from_meta({'cid': cid, 'uid': uid})
        self.root = Path(f'~/.qq_music/{uid}')

    def update_all(self):
        for album in self.album_collection:
            if album in self:
                break

            self.set_album(album)
            for song in album:
                self.set_song(album, song)

    def set_album(self, album: Album):
        album_dir = self.root / album.name
        album_dir.mkdir()

        album_meta_filename = album_dir / 'meta.json'
        with album_meta_filename.open('w+') as f:
            json.dump(f, album.to_json())

    def set_song(self, album: Album, song: Song):
        song_dir = self.root / album.name / song.name
        song_dir.mkdir()

        song_meta_filename = song_dir / 'meta.json'
        with song_meta_filename.open('w+') as f:
            json.dump(f, song.to_json())

    def search(self, artist: str, title: str):
        for album_dir in self.root.walk():
            for song_dir in album_dir.walk():
                song_meta_filename = song_dir / 'meta.json'
                with song_meta_filename.open() as f:
                    song = Song.from_json(json.load(f))
                    if song.match(artist, title):
                        return song

    def __contains__(self, album: Album):
        album_dir = self.root / album.name
        return album_dir.exists()


class QQMusic:
    def __init__(self, cid, uid):
        self.cache = QQMusicCache(cid, uid)

    def search(self, artist: str, title: str):
        if not self.cache.search(artist, title):
            self.cache.update_all()

        return self.cache.search(artist, title)
