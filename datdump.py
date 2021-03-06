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


trackers = []
first_parties = {}


def read_string(data, length=None):
    if not length:
        length = data.find(0)
    # TODO: deal with -1
    return "".join(chr(c) for c in data[:length])


def hex_to_number(hexstring):
    #print("hexstring = %s" % hexstring)
    return int(hexstring, 16)


def read_value(data):
    pos = 0
    value_length_string = read_string(data[pos:])
    value_length = hex_to_number(value_length_string)
    pos += len(value_length_string)+1

    value = read_string(data[pos:], value_length)
    pos += value_length
    return (value, pos)


# https://github.com/bbondy/hashset-cpp/blob/f86b0a5752545274e32c0dbb654c3592cc131c8a/hash_set.h#L232-L285
def parse_hashset(data, size, group_first_parties):
    pos = 0

    s = read_string(data[pos:])
    #print('metadata = %s' % s)
    comma = s.find(',')
    nb_buckets = hex_to_number(s[:comma])
    multiset = hex_to_number(s[comma+1:])
    #print("nb_buckets = %s" % nb_buckets)
    pos += len(s)+1

    for i in range(nb_buckets):
        if pos >= size:
            print("ERROR: size '%s' is invalid" % size, file=sys.stderr)
            return

        while data[pos:].find(0) != 0:
            if pos >= size:
                print("ERROR: size '%s' is invalid" % size, file=sys.stderr)
                return

            if group_first_parties:
                # TODO: group first party and related domains
                (key, length) = read_value(data[pos:])
                pos += length
                (value, length) = read_value(data[pos:])
                pos += length
                sorted_value = sorted(value.split(","))
                first_parties[key] = ",".join(sorted_value)
            else:
                (value, length) = read_value(data[pos:])
                pos += length
                trackers.append(value)

        pos += 1


def parse_file(datfile):
    data = Path(datfile).read_bytes()
    pos = 0

    s = read_string(data[pos:])
    pos += len(s)+1
    trackers_size = hex_to_number(s)
    #print("trackers_size = %s" % trackers_size)

    parse_hashset(data[pos:], trackers_size, False)

    pos += trackers_size
    s = read_string(data[pos:])
    pos += len(s)+1
    first_parties_size = hex_to_number(s)
    #print("first_parties_size = %s" % first_parties_size)

    parse_hashset(data[pos:], first_parties_size, True)


def print_trackers():
    print("nb_trackers = " + str(len(trackers)))
    for v in sorted(trackers):
        print(v)


def print_first_parties():
    print("nb_first_parties = " + str(len(first_parties)))
    for k in sorted(first_parties):
        print(k + ": " + first_parties[k])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('datfile', type=str, help='the file to dump')
    args = parser.parse_args()

    # Validate the parameters
    if not os.path.isfile(args.datfile):
        print("Error: '%s' not found" % args.datfile, file=sys.stderr)
        return 1

    parse_file(args.datfile)
    print_trackers()
    print()
    print_first_parties()
    return 0


exit(main())
