import click

from .utils import DirType
from .libs.music import Music
from .libs.qq_music import QQMusic


@click.command()
@click.option('-f', '--music-file', type=click.Path(exists=True))
@click.option('-d', '--music-dir', type=DirType())
def musik(music_file, music_dir, qq_cookies):
    qq_music = QQMusic(qq_cookies)

    if music_file:
        music = Music.from_filename(music_file)
        music.fetch_info_from_qq(qq_music)

    elif music_dir:
        for music_filename in music_dir.glob('.mp3'):
            music = Music.from_filename(music_filename)
            music.fetch_info_from_qq(qq_music)
        music_dir.refine()

    else:
        raise ValueError('must specify --music-file or --music-dir')


if __name__ == '__main__':
    musik()
