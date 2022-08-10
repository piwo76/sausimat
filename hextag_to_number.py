from sausimat.start import hex_tag_to_nr
import argparse

parser = argparse.ArgumentParser(description='Hex Tag to number')
parser.add_argument('tag', type=str, help='the playlist name')
args = parser.parse_args()

number_tag = hex_tag_to_nr(args.tag)
print(number_tag)