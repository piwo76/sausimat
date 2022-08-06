from sausimat.sausimat import Sausimat
from sausimat.start import hex_tag_to_nr
import argparse

parser = argparse.ArgumentParser(description='Hex Tag to number')
parser.add_argument('--arduino-serial', type=str, default='/dev/ttyUSB0', help='the arduino serial found in /dev/tty*')
parser.add_argument('--baud-rate', type=int, default=9600, help='the arduino baud rate')
parser.add_argument('--logfile', type=int, default='/var/log/sausimat.log', help='the path to the logfile')

args = parser.parse_args()

sausimat = Sausimat(dev=args.arduino_serial, baud_rate=args.baud_rate, logfile=args.logfile)
sausimat.run()
