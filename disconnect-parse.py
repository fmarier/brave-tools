#!/usr/bin/env python3
# -*- mode: python -*-
#
# Parser for the Disconnect tracking protection list:
#  https://github.com/disconnectme/disconnect-tracking-protection/blob/master/services.json
#
# WARNING WARNING WARNING
#
# This parser doesn't have any error checking, do not use it with
# untrusted input! It's only meant for debugging purposes.

import argparse
import json
import os
import sys


EXCLUDED_CATEGORIES = ['Content']
trackers = set()


def parse_category(category):
    for i in range(len(category)):
        for org in category[i]:
            for url in category[i][org]:
                if url[:7] != 'http://' and url[:8] != 'https://':
                    continue

                for tracker in category[i][org][url]:
                    #print("%s (%s): %s" % (org, url, tracker))
                    trackers.add(tracker)


def parse_file(jsonfile):
    with open(jsonfile, 'r') as f:
        data = json.loads(f.read())
        for category in data['categories']:
            if category in EXCLUDED_CATEGORIES:
                continue
            parse_category(data['categories'][category])


def print_trackers():
    print("nb_trackers = " + str(len(trackers)))
    for v in sorted(trackers):
        print(v)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('jsonfile', type=str, help='the file to dump')
    args = parser.parse_args()

    # Validate the parameters
    if not os.path.isfile(args.jsonfile):
        print("Error: '%s' not found" % args.jsonfile, file=sys.stderr)
        return 1

    parse_file(args.jsonfile)
    print_trackers()
    return 0


exit(main())
