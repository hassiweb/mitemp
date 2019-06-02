#!/usr/bin/env python3

import argparse
import re
import logging
import sys
import os
import json
from datetime import datetime as dt

from btlewrap import available_backends, BluepyBackend, GatttoolBackend, PygattBackend
from mitemp_bt.mitemp_bt_poller import MiTempBtPoller, \
    MI_TEMPERATURE, MI_HUMIDITY, MI_BATTERY


def valid_mitemp_mac(mac, pat=re.compile(r"(4C:65:A8|58:2D:34):[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}")):
    """Check for valid mac adresses."""
    if not pat.match(mac.upper()):
        raise argparse.ArgumentTypeError('The MAC address "{}" seems to be in the wrong format'.format(mac))
    return mac


def poll(args):
    """Poll data from the sensor."""
    backend = _get_backend(args)
    poller = MiTempBtPoller(args.mac, backend)
    print("Getting data from Mi Temperature and Humidity Sensor")
    print("FW: {}".format(poller.firmware_version()))
    print("Name: {}".format(poller.name()))
    print("Battery: {}".format(poller.parameter_value(MI_BATTERY)))
    print("Temperature: {}".format(poller.parameter_value(MI_TEMPERATURE)))
    print("Humidity: {}".format(poller.parameter_value(MI_HUMIDITY)))

    dtnow = dt.now()
    data = { \
                dtnow.strftime('%Y/%m/%d %H:%M:%S'): { \
                    'MAC': args.mac, \
                    'Battery': poller.parameter_value(MI_BATTERY), \
                    'Temperature': poller.parameter_value(MI_TEMPERATURE), \
                    'Humidity': poller.parameter_value(MI_HUMIDITY) \
                } \
            }

    data = append_json_to_file(data, args.location + os.sep + args.mac + '.json')


def append_json_to_file(_dict, path_file):
    with open(path_file, 'ab+') as f:
        f.seek(0,2)
        if f.tell() == 0:
            f.write(json.dumps([_dict]).encode())
        else :
            f.seek(-1,2)
            f.truncate()
            f.write(' , '.encode())
            f.write(json.dumps(_dict).encode())
            f.write(']'.encode())
    return f.close()



# def scan(args):
#     """Scan for sensors."""
#     backend = _get_backend(args)
#     print('Scanning for 10 seconds...')
#     devices = mitemp_scanner.scan(backend, 10)
#     devices = []
#     print('Found {} devices:'.format(len(devices)))
#     for device in devices:
#         print('  {}'.format(device))


def _get_backend(args):
    """Extract the backend class from the command line arguments."""
    if args.backend == 'gatttool':
        backend = GatttoolBackend
    elif args.backend == 'bluepy':
        backend = BluepyBackend
    elif args.backend == 'pygatt':
        backend = PygattBackend
    else:
        raise Exception('unknown backend: {}'.format(args.backend))
    return backend


def list_backends(_):
    """List all available backends."""
    backends = [b.__name__ for b in available_backends()]
    print('\n'.join(backends))


def main():
    """Main function.

    Mostly parsing the command line arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--backend', choices=['gatttool', 'bluepy', 'pygatt'], default='gatttool')
    parser.add_argument('-v', '--verbose', action='store_const', const=True)
    subparsers = parser.add_subparsers(help='sub-command help', )

    parser_poll = subparsers.add_parser('poll', help='poll data from a sensor')
    parser_poll.add_argument('mac', type=valid_mitemp_mac)
    parser_poll.add_argument('location', help='location to save a received data file (JSON)')
    parser_poll.set_defaults(func=poll)

    # parser_scan = subparsers.add_parser('scan', help='scan for devices')
    # parser_scan.set_defaults(func=scan)

    parser_scan = subparsers.add_parser('backends', help='list the available backends')
    parser_scan.set_defaults(func=list_backends)
    
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == '__main__':
    main()
