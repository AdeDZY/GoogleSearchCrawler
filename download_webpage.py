import sys
import json
reload(sys)
sys.setdefaultencoding('utf-8')

import urllib2, socket, time
import gzip, StringIO
import re, random, types
import argparse
import thread


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("docid_url_file", help="Each line is a docid tab url")
    parser.add_argument("usr_agent_file")
    parser.add_argument("fout", type=argparse.FileType('w'))
    args = parser.parse_args()

    # read agents
    user_agents = [line.strip() for line in open(args.usr_agent_file).readlines()]
    n_urls = 0
    failed_urls = 0

    with open(args.docid_url_file) as f:
        for line in f:
            docid, url = line.strip().split('\t')
            url = urllib2.unquote(url)
            if '.pdf' in url:
                continue
            print url
            n_urls += 1
            try:
                length = len(user_agents)
                index = random.randint(0, length - 1)
                user_agent = user_agents[index]

                request = urllib2.Request(url)
                request.add_header('User-agent', user_agent)
                request.add_header('Accept-Encoding', 'gzip')
                request.add_header('connection', 'keep-alive')

                response = urllib2.urlopen(request, timeout=10)
                html = response.read()
                if response.headers.get('content-encoding', None) == 'gzip':
                    html = gzip.GzipFile(fileobj=StringIO.StringIO(html)).read()
                args.fout.write(docid + '\n')
                args.fout.write(html)
                args.fout.write('\n')
            except urllib2.URLError, e:
                print 'url error:', e, url
                failed_urls += 1
                continue
            except Exception, e:
                failed_urls += 1
                print 'error:', e
                continue
            if n_urls % 10 == 0:
                print n_urls, failed_urls

    args.fout.close()
