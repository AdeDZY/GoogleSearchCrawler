
import sys

reload(sys)
sys.setdefaultencoding('utf-8')
import urllib2
import argparse
import json

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("search_file")
    parser.add_argument("query_file")
    parser.add_argument("id2url_file")
    parser.add_argument("parsed_body_file")
    parser.add_argument("output_file", type=argparse.FileType('w'))
    args = parser.parse_args()

    query2qid = {}
    for qid, line in enumerate(open(args.query_file)):
        query2qid[line.strip()] = qid + 1

    url2id = {}
    for line in open(args.id2url_file):
        docid, url = line.strip().split('\t')
        url2id[url] = docid

    docid2body = {}
    for line in open(args.parsed_body_file):
        items = line.strip().split('\t')
        docid = items[0].strip()
        title = items[1]
        body = ' '.join(items[2:])
        docid2body[docid] = body

    rank = -1
    prev_qid = -1
    for line in open(args.search_file):
        obj = json.loads(line)
        assert 'doc' in obj, line
        assert 'url' in obj['doc'], line

        url = obj['doc']['url']
        snippet = obj['doc']['snippet']
        query = obj['query']
        title = obj['doc']['title']

        assert query in query2qid, line
        qid = query2qid[query]

        assert url in url2id, line
        docid = url2id[url]

        body = docid2body.get(docid, '')
        obj2 = {"query": query, "doc": {"url": url, "title": title, "snippet": snippet, 'body': body}}
        jstr = json.dumps(obj2)

        if qid != prev_qid:
            prev_qid = qid
            rank = 0
        rank += 1
        outline = "{0}\tQ0\t{1}\t{2}\t{3}\tindri # {4}\n".format(qid, docid, rank, -rank, jstr)
        args.output_file.write(outline)




