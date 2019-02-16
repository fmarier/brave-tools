#!/usr/bin/env python3
# -*- mode: python -*-
#
# Parser for the Mozilla tracking protection entity list:
#  https://github.com/mozilla-services/shavar-prod-lists/blob/master/disconnect-entitylist.json
#
# WARNING WARNING WARNING
#
# This parser doesn't have any error checking, do not use it with
# untrusted input! It's only meant for debugging purposes.

import argparse
import json
import os
import sys


first_parties = {}


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
        for org in data:
            resources = []
            for resource in data[org]['resources']:
                resources.append(resource)
            for property in data[org]['properties']:
                #print("%s: %s = %s" % (org, property, ",".join(resources)))
                first_parties[property] = sorted(resources)


def print_first_parties():
    print("nb_first_parties = " + str(len(first_parties)))
    for v in sorted(first_parties):
        print("%s: %s" % (v, ",".join(first_parties[v])))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('jsonfile', type=str, help='the file to dump')
    args = parser.parse_args()

    # Validate the parameters
    if not os.path.isfile(args.jsonfile):
        print("Error: '%s' not found" % args.jsonfile, file=sys.stderr)
        return 1

    parse_file(args.jsonfile)
    print_first_parties()
    return 0


exit(main())
