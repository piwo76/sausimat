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

def hex_tag_to_nr(hex_tag):
    splitted_tag = hex_tag.split(' ')
    if len(splitted_tag) != 4:
        raise ValueError('Wrong tag format')

    hex_int = []
    for h in splitted_tag:
        h = '0x' + h
        hex_int.append(int(h, 16))
    r = MFRC522Sausimat()
    serial_number_check = 0
    for i in range(4):
        serial_number_check = serial_number_check ^ hex_int[i]
    hex_int.append(serial_number_check)
    return r.uid_to_num(hex_int)


def run():
    sausimat = Sausimat()
    sausimat.run()

def rescan_library():
    mopidy = SausimatMopidy()
    print('rescanning library...')
    mopidy.rescan_local_library()
    print('done!')

def create_playlist():
    #logger = logging.getLogger('sausimat')
    #logger.info(f'Stopping Sausimat...')
    #subprocess.run(["sudo", "systemctl", "stop", "sausimat.service"])
    #sleep(5)

    tag = None
    manual_tag = True if input('%s (y/N)? ' % 'Manually enter tag').lower() == 'y' else False
    if manual_tag:
        tag = input('Enter hex tag in for XX XX XX XX: ')
        tag = hex_tag_to_nr(tag)

    name = input('Playlist Name: ')
    dir = input('Directory: ')
    overwrite = True if input('%s (y/N): ' % 'Overwrite').lower() == 'y' else False
    repeat = True if input('%s (y/N): ' % 'Repeat').lower() == 'y' else False
    shuffle = True if input('%s (y/N): ' % 'Shuffle').lower() == 'y' else False
    if not tag:
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

