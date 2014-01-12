#!/usr/bin/python

"""
Copyright CrowdGrader LLC, 2014

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import getopt
import json
import os
import os.path
import sys

def usage():
    print "Usage: download_assignment.py <assignment_file.json> <destination_directory>"


def main():
    try:
        opts, args = getopt.getopt(sys.argv[3:], "", [])
    except getopt.GetoptError, e:
        print str(e)
        usage()
        sys.exit(2)

    if len(sys.argv) < 3:
        usage()
        sys.exit(2)

    json_file_name = sys.argv[1]
    dest_dir = sys.argv[2]
    if check_directory_exists(dest_dir):
        print "Error: Destination directory already exists."
        sys.exit(1)

    assignment_data = read_json_file(json_file_name)
    write_assignment_data(assignment_data)
    download_submissions(assignment_data)
    download_reviews(assignment_data)

    print "All assignment data downloaded."


def check_directory_exists(dir_name):
    return os.path.isdir(dir_name)


def read_json_file(json_file_name):
    """Reads the json file containing the assignment data."""
    try:
        f = open(json_file_name, 'r')
        d = json.loads(f.read())
        return d
    except Exception, e:
        print "Error:", e
        sys.exit(2)


def write_assignment_data(assignment_data):
    """Writes in human-readable form the main data of the assignment."""
    pass


def download_submissions(assignment_data):
    """Downloads all the submissions to the assignment, each into their own directory."""
    pass


def download_reviews(assignment_data):
    """Downlads the reviews that each of the submissions received."""
    pass


if __name__ == '__main__':
    main()
