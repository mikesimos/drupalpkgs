#!/usr/bin/env python

#   This file is part of drupalpkgs.
#
#   drupalpkgs is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 2 of the License, or
#   (at your option) any later version.
#
#   drupalpkgs is distributed in the hope that it will be useful, but
#   WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#   GNU General Public License for more details.
#   You should have received a copy of the GNU General Public License
#   along with drupalpkgs. If not, see: <http://www.gnu.org/licenses/>.
#
# Authors:
# version 0.1 Michael-Angelos Simos

"""
Simple python script for listing Drupal 7 module module packages dependencies along with their respective versions.
"""

from __future__ import print_function
from argparse import ArgumentParser
from subprocess import Popen, PIPE


class Colors:
    def __init__(self):
        pass
    header = '\033[95m'
    blue = '\033[94m'
    green = '\033[92m'
    yellow = '\033[93m'
    red = '\033[91m'
    end = '\033[0m'
    strong = '\033[1m'
    underline = '\033[4m'


class DrupalPackages:

    def __init__(self, drupal_root_path='', uri=''):
        """
        :param str drupal_root_path: The root path of Drupal core
        :param str uri: A website uri
        """
        self.mods = {}
        self.drupal_root_path = drupal_root_path
        self.uri = uri

    def extract_pkgs(self):
        """
        List Drupal 7 enabled modules along with their respective packages and versions
        :return: None
        """
        cmd = "drush pml --root={} --uri={} --type=Module --no-core|grep Enabled"\
              .format(self.drupal_root_path, self.uri)
        p = Popen(cmd, shell=True, stdout=PIPE)
        if not p.stderr:
            for i in p.stdout.read().split('\n'):
                if i:
                    module_name = i.split()[-3].replace(')', '').replace('(', '')
                    cmd = "drush pmi {} --root={} --uri={}"\
                          .format(module_name.lower(), self.drupal_root_path, self.uri)
                    mod_info = Popen(cmd, shell=True, stdout=PIPE)
                    module_project = ''
                    module_version = ''
                    if not mod_info.stderr:
                        for l in mod_info.stdout.read().split('\n'):
                            if 'Project ' in l:
                                module_project = l.split()[-1]
                            if 'Version ' in l:
                                module_version = l.split()[-1]
                        if module_project + '-' + module_version in self.mods:
                            self.mods[module_project + '-' + module_version].append(module_name + '-' + module_version)
                        else:
                            self.mods[module_project + '-' + module_version] = [module_name + '-' + module_version, ]
                    else:
                        print(Colors.red, mod_info.stderr.read(), Colors.end)
            return self.mods
        else:
            print (Colors.red, p.stderr.read(), Colors.end)


def get_args():
    """
    Return Command Line Arguments.
    :return: ArgumentParser instance
    """
    parser = ArgumentParser(description="Simple tool for listing Drupal 7 enabled modules along with their "
                                        "respective packages and versions",)
    parser.add_argument('-r', '--drupal_root', required=True, help='Drupal root path')
    parser.add_argument('-u', '--uri', required=True, help='Website uri')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose Mode')
    return parser.parse_args()


def main():

    # - Get command line args and config args.
    args = get_args()
    pkgs = DrupalPackages(args.drupal_root, args.uri).extract_pkgs()

    if args.verbose:
        print("##################")
        print(Colors.strong, "Found modules:", Colors.end)
        print(Colors.blue, "Package Name:\t\t", Colors.end, "[Modules]")
        for p, v in pkgs.iteritems():
            print (Colors.blue, p, Colors.end, ":\t\t", v)
        print(Colors.end)
    print("##################")
    print(Colors.strong, "Drush command:", Colors.end)
    print(Colors.green, "drush dl ", end="")
    for p in pkgs.iterkeys():
        print (p, " ", end="")
    print(Colors.end)


if __name__ == "__main__":
    main()

