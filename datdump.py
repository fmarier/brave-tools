#!/usr/bin/env python3
# -*- mode: python -*-
#
# WARNING WARNING WARNING
#
# This parser doesn't have any error checking, do not use it with
# untrusted input! It's only meant for debugging purposes.

import argparse
import os
import sys

from pathlib import Path


def read_string(data, length=None):
    if not length:
        length = data.find(0)
    # TODO: deal with -1
    return "".join(chr(c) for c in data[:length])

def hex_to_number(hexstring):
    #print("hexstring = %s" % hexstring)
    return int(hexstring, 16)

# https://github.com/bbondy/hashset-cpp/blob/f86b0a5752545274e32c0dbb654c3592cc131c8a/hash_set.h#L232-L285
def parse_trackers(data, size):
    pos = 0

    s = read_string(data[pos:])
    #print('metadata = %s' % s)
    comma = s.find(',')
    nb_buckets = hex_to_number(s[:comma])
    multiset = hex_to_number(s[comma+1:])  # unused
    #print("nb_buckets = %s" % nb_buckets)
    pos += len(s)+1

    for i in range(nb_buckets):
        host_length_string = read_string(data[pos:])
        if len(host_length_string) > 0:
            host_length = hex_to_number(host_length_string)
            pos += len(host_length_string)+1

            host = read_string(data[pos:], host_length)
            print(host)
            pos += host_length
        else:
            pos += 1

def parse_file(datfile):
    data = Path(datfile).read_bytes()
    pos = 0

    s = read_string(data[pos:])
    pos += len(s)+1
    trackers_size = hex_to_number(s)
    print("trackers_size = %s" % trackers_size)

    parse_trackers(data[pos:], trackers_size)

    pos += trackers_size
    s = read_string(data[pos:])
    pos += len(s)+1
    first_parties_size = hex_to_number(s)
    print("first_parties_size = %s" % first_parties_size)

    # TODO: parse_first_parties(data[pos:], first_parties_size)

    #i = int.from_bytes(data[:4], byteorder='little', signed=False)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('datfile', type=str, help='the file to dump')
    args = parser.parse_args()

    # Validate the parameters
    if not os.path.isfile(args.datfile):
        print("Error: '%s' not found" % args.datfile, file=sys.stderr)
        return 1

    parse_file(args.datfile)
    return 0

exit(main())
