import re
import json
from pathlib import Path
from operator import itemgetter
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
        resp = requests.get(cls.URL_FORMATTER(meta))
        resp.raise_for_status()
        details = json.loads(re.search(r'{.+}', resp.content.decode()).group())
        return cls(meta, details)

    def __init__(self, meta: dict, details: Optional[dict] = None):
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
    URL_FORMATTER = 'https://c.y.qq.com/fav/fcgi-bin/fcg_get_profile_order_asset.fcg?loginUin=0&hostUin=0&format=jsonp&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0&ct=20&cid={cid}&userid={uid}&reqtype=2&ein=1000'.format_map

    def __iter__(self):
        for album_meta in self.details['data']['albumlist']:
            album = Album.from_meta(album_meta)
            yield album


class Album(Resource):
    URL_FORMATTER = 'https://c.y.qq.com/v8/fcg-bin/fcg_v8_album_info_cp.fcg?loginUin=0&hostUin=0&format=jsonp&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0&albummid={albummid}&jsonpCallback=albuminfoCallback'.format_map

    def search(self, artist, title):
        for song in self.details['data']['list']:
            if song['songname'] == title and artist in {
                    singer['name']
                    for singer in song['singer']
            }:
                return song

    @property
    def name(self):
        return self.meta['albumname']


class QQMusicCache:
    def __init__(self, cid, uid):
        self.album_collection = AlbumCollection.from_meta({
            'cid': cid,
            'uid': uid
        })
        self.root = Path.home() / f'.qq_music/{uid}'

    def update_all(self):
        for album in self.album_collection:
            if album in self:
                break

            self.set_album(album)

    def set_album(self, album: Album):
        album_dir = self.root / album.name
        album_dir.mkdir(parents=True)

        album_meta_filename = album_dir / 'meta.json'
        with album_meta_filename.open('w+') as f:
            json.dump(album.to_json(), f)

    def search(self, artist: str, title: str):
        for album_dir in self.root.glob('*'):
            album_meta_filename = album_dir / 'meta.json'
            album = Album.from_file(album_meta_filename)
            song = album.search(artist, title)
            if song:
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
