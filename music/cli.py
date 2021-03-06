import click

from .utils import DirType
from .libs.music import Music
from .libs.qq_music import QQMusic


@click.command()
@click.option('-f', '--music-file', type=click.Path(exists=True))
@click.option('-d', '--music-dir', type=DirType())
@click.option('-c', '--qq-cid')
@click.option('-u', '--qq-uid')
def musik(music_file, music_dir, qq_cid, qq_uid):
    qq_music = QQMusic(qq_cid, qq_uid)

    if music_file:
        music = Music.from_filename(music_file)
        music.update_from_qqmusic(qq_music)

    elif music_dir:
        for music_filename in music_dir.glob('.mp3'):
            music = Music.from_filename(music_filename)
            music.fetch_info_from_qq(qq_music)
        music_dir.refine()

    else:
        raise ValueError('must specify --music-file or --music-dir')


if __name__ == '__main__':
    try:
        musik()
    except:
        import sys, pdb, traceback
        _, _, tb = sys.exc_info()
        traceback.print_exc()
        pdb.post_mortem(tb)
