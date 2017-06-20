import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("trec_in")
    parser.add_argument("topn_as_rel", type=int)
    parser.add_argument("--by_rank", action="store_true")
    args = parser.parse_args()

    prev_qid = -1
    rank = 0
    rel = 0

    for line in open(args.trec_in):
        items = line.split('\t')
        qid = int(items[0])
        docid = items[2]
        if qid != prev_qid:
            prev_qid = qid
            rank = 0
        rank += 1
        if rank > args.topn_as_rel:
            rel = 0
        if args.by_rank and rank <= args.topn_as_rel:
            rel = (args.topn_as_rel + 1) - rank
        print "{0} 0 {1} {2}".format(qid, docid, rel)


