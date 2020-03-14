import json
import logging
import subprocess
from time import sleep

from sausimat.mfrc522 import MFRC522Sausimat

from sausimat.mopidy import SausimatMopidy

from sausimat.sausimat import Sausimat

def read_rfid():
    rdr = MFRC522Sausimat()
    while True:
        id, text = rdr.read_no_block()
        if id:
            return id

def run():
    sausimat = Sausimat()
    sausimat.run()

def rescan_library():
    mopidy = SausimatMopidy()
    print('rescanning library...')
    mopidy.rescan_local_library()
    print('done!')

def create_playlist():
    logger = logging.getLogger('sausimat')
    logger.info(f'Stopping Sausimat...')
    subprocess.run(["sudo", "systemctl", "stop", "sausimat.service"])
    sleep(5)

    name = input('Playlist Name: ')
    dir = input('Directory: ')
    overwrite = True if input('%s (y/N): ' % 'Overwrite').lower() == 'y' else False
    repeat = True if input('%s (y/N): ' % 'Repeat').lower() == 'y' else False
    shuffle = True if input('%s (y/N): ' % 'Shuffle').lower() == 'y' else False
    print('Please hold the new card to the reader...')
    tag = read_rfid()
    print(f'The new cards id is: {tag}')



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

