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
import re
import urllib2
import sys

def usage():
    print "Usage: download_assignment.py <assignment_file.json> <destination_directory>"


# Mapping from emails to (first_name, last_name) pairs.
email_to_names = {}


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
    write_assignment_data(dest_dir, assignment_data)

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


def make_directory(dir_name):
    if not check_directory_exists(dir_name):
        os.makedirs(dir_name)


def write_assignment_data(dir_name, d):
    """Writes in human-readable form the main data of the assignment."""
    make_directory(dir_name)
    f = open(os.path.join(dir_name, "info.txt"), 'w')
    f.write("Assignment: %r\n" % d.get('Assignment'))
    f.write("Number of submissions: %d\n" % len(d.get('Submission list', [])))
    f.close()
    # Generates a hash mapping from email to (first, last) names,
    # useful to print better info on submissions.
    for subm in d.get('Submission list', []):
        email_to_names[subm.get('User email')] = (
            subm.get('First name'), subm.get('Last name'))
    for subm in d.get('Submission list', []):
        download_submissions(dir_name, subm)
        

def download_submissions(dir_name, subm):
    """Downloads a submission into its own directory."""
    # First, creates the directory.
    print "Downloading submission for:", subm.get('User email')
    subm_dir_name = os.path.join(dir_name, subm.get('User email', 'unknown-user'))
    make_directory(subm_dir_name)
    f = open(os.path.join(subm_dir_name, "info.txt"), 'w')
    f.write("Email: %r\n" % subm.get('User email'))
    f.write("First name: %r\n" % subm.get('First name'))
    f.write("Last name: %r\n" % subm.get('Last name'))
    f.write("Submission date:%r\n" % subm.get('Submission date'))
    subm_link = subm.get('Submitted link')
    if subm_link is not None:
        f.write("Submitted link: %r\n" % subm_link)
    else:
        f.write("No submitted link.\n")
    upload_url = subm.get('Uploaded file')
    if upload_url is None:
        f.write("No uploaded file.\n")
    members = subm.get('Group members')
    if members is not None:
        for m in members:
            (first_name, last_name) = email_to_names.get(m, ('', ''))
            f.write("    Group member: %r : %r %r\n" % (m, first_name, last_name))
    f.close()
    # Downloads the submission itself.
    text_url = subm.get('Submission')
    download_text(subm_dir_name, text_url, name='submission.txt')
    # Downloads any uploaded file.
    download_file(subm_dir_name, upload_url, name='attachment.txt')
    # Downloads any reviews.
    download_reviews(subm_dir_name, subm)


def download_reviews(subm_dir_name, subm):
    """Downlads the reviews for a given submission."""
    print "Downloading reviews..."
    w, _ = my_url_open(subm.get('Reviews'))
    f = open(os.path.join(subm_dir_name, "reviews.txt"), 'w')
    revs = json.loads(w)
    for r in revs.get('Reviews'):
        f.write("Review by: %r on: %r\n" % (r.get('Review author'), 
                                            r.get('Completed date')))
        f.write("Declined: %s\n" % str(r.get('Declined')))
        f.write("Grade: %r\n" % r.get('Review grade'))
        f.write("Helpfulness: %r\n\n" % r.get('Review helpfulness'))
        f.write("Review:\n\n")
        f.write(tostring(r.get('Reviewer comments')))
        f.write("\n\n")
        if r.get('Review feedback') is not None:
            f.write("\nFeedback:\n\n")
            f.write("%s" % tostring(r.get('Review feedback')))
            f.write("\n\n")
        f.write("==============================\n\n")
    f.close()
    

def download_text(dir_name, url, name='submission.txt'):
    w, _ = my_url_open(url)
    sub = json.loads(w)
    f = open(os.path.join(dir_name, name), 'w')
    f.write('%s' % tostring(sub.get('Submission')))
    f.close()


def download_file(dir_name, url, name='attachment.txt'):
    if url is None:
        return
    w, h = my_url_open(url)
    filename = get_original_filename(h, name=name)
    print "Downloading:", filename
    f = open(os.path.join(dir_name, filename), 'w')
    f.write(w)
    f.close()
    

def get_original_filename(h, name="attachment.txt"):
    for el in h:
        if el.startswith('Content-Disposition:'):
            filename = re.findall("filename=(\S+)", el)            
            if filename is not None and len(filename) > 0:
                return filename[0][1:-1]
    return name


def my_url_open(url, n_retries=3):
    request = urllib2.Request(url)
    for i in range(n_retries):
        try:
            w = urllib2.urlopen(request)
            return w.read(), w.info().headers
        except Exception, e:
            print "Error in download:", e
        print "Retrying"
    print "Failed"
    return '', []


def tostring(s):
    t = s.encode('utf-8', 'ignore')
    return t.replace('\r\n', os.linesep)

if __name__ == '__main__':
    main()
