from sausimat.start import create_playlist2
import argparse

parser = argparse.ArgumentParser(description='Create Playlist')
parser.add_argument('name', type=str, help='the playlist name')
parser.add_argument('dir', type=str, help='the directory of the media files')
parser.add_argument('--tag-hex', type=str, default=None, help='the tag in hex format')
parser.add_argument('--tag-number', type=str, default=None, help='the tag in decimal format')
parser.add_argument('--overwrite', type=bool, default=True, help='overwrite the playlist if exists')
args = parser.parse_args()

create_playlist2(args.name, args.dir, args.tag_hex, args.tag_number, args.overwrite)
