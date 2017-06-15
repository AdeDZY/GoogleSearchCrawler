import sys
import json
reload(sys)
sys.setdefaultencoding('utf-8')

import urllib2, socket, time
import gzip, StringIO
import re, random, types
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("in_json_file")
    parser.add_argument("output_docid_url_file")
    parser.add_argument("--start_id", "-s", type=int, default=0)
    parser.add_argument("--prefix", "-p", default="google-2017")
    args = parser.parse_args()

    intid = args.start_id
    outfile = open(args.output_docid_url_file, 'w')
    for line in open(args.in_json_file):
        obj = json.loads(line)
        assert 'doc' in obj, line
        assert 'url' in obj['doc'], line
        url = obj['doc']['url']
        extid = args.prefix + '-{0}'.format(intid)
        outfile.write('{0}\t{1}\n'.format(extid, url))
        intid += 1

