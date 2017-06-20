import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("first_trec")
    parser.add_argument("second_trec")
    parser.add_argument("output_file", type=argparse.FileType('w'))
    args = parser.parse_args()

    # read first
    trec = {}
    for line in open(args.first_trec):
        items = line.split('\t')
        qid = int(items[0])
        if qid not in trec:
            trec[qid] = {}
        trec[qid].append(line)

    # read second
    for line in open(args.second_trec):
        items = line.split('\t')
        qid = int(items[0])
        if qid not in trec:
            continue
        trec[qid].append(line)

    # merge
    for qid in trec:
        for line in trec[qid]:
            args.out_file.write(line)

