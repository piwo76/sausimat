import argparse
import json

from sausimat.mopidy import SausimatMopidy

from sausimat.sausimat import Sausimat


def run():
    sausimat = Sausimat()
    sausimat.run()

def rescan_library():
    mopidy = SausimatMopidy()
    print('rescanning library...')
    mopidy.rescan_local_library()
    print('done!')

def create_playlist():
    parser = argparse.ArgumentParser()

    parser.add_argument('name')
    parser.add_argument('directory')
    parser.add_argument('--overwrite', default=True)
    parser.add_argument('--tag', default=None)
    parser.add_argument('--repeat', default=False)
    parser.add_argument('--shuffle', default=False)
    args = parser.parse_args()

    dir = args.directory.replace('/media/', '')
    if dir[-1] == '/':
        dir = dir[:-1]

    mopidy = SausimatMopidy()
    #mopidy.rescan_local_library()

    mopidy.create_playlist(args.name, search_string=f'{dir}/*', overwrite=args.overwrite)

    if args.tag:
        content = {'playlist': args.name, 'repeat': args.repeat, 'shuffle': args.shuffle}
        with open(f'/media/playlists/{args.tag}.json', 'w') as outfile:
            json.dump(content, outfile)

run()
