import json
import logging
import subprocess
from time import sleep

from sausimat.mopidy import SausimatMopidy

from sausimat.sausimat import Sausimat


def hex_tag_to_nr(hex_tag):
    splitted_tag = hex_tag.split()
    return Sausimat.uid_to_num(splitted_tag)


def run():
    sausimat = Sausimat()
    sausimat.run()


def rescan_library():
    mopidy = SausimatMopidy()
    print('rescanning library...')
    mopidy.rescan_local_library()
    print('done!')


def create_playlist2(name, dir, tag_hex=None, tag_number=None, overwrite=True):
    logger = logging.getLogger('sausimat')
    logger.info(f'Stopping Sausimat...')
    subprocess.run(["sudo", "systemctl", "stop", "sausimat.service"])
    sleep(5)

    tag = None
    if tag_hex:
        tag = hex_tag_to_nr(tag_hex)
    elif tag_number:
        tag = tag_number

    repeat = False
    shuffle = False

    dir = dir.replace('/media/', '')
    if dir[-1] == '/':
        dir = dir[:-1]

    mopidy = SausimatMopidy()

    mopidy.create_playlist(name, search_string=f'{dir}/*', overwrite=overwrite)

    if tag:
        content = {'playlist': name, 'repeat': repeat, 'shuffle': shuffle}
        with open(f'/media/playlists/{tag}.json', 'w') as outfile:
            json.dump(content, outfile)
    subprocess.run(["sudo", "systemctl", "start", "sausimat.service"])
    sleep(5)
