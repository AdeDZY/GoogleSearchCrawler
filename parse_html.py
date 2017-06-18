#!/bos/usr0/zhuyund/bin/python2.7
import argparse
from boilerpipe.extract import Extractor

import logging
import traceback
import string
import re
from os import listdir, makedirs
from os.path import isfile, join, exists


class Reader:
    """
    Read web files and give document raw text
    """

    def __init__(self, file_path):
        self.f = open(file_path)
        self.docno = self.f.readline().strip()

    def __iter__(self):
        return self

    def next(self):
        """
        :return: the next document
        """

        lines = []
        line = self.f.readline()
        if not line:
            raise StopIteration()
        lines.append(line)
        while True:
            line = self.f.readline()
            if "google-2017" in line:
                docno = self.docno
                self.docno = line.strip()
                html_text = ' '.join(lines)
                return docno, html_text
            if not line:
                docno = self.docno
                html_text = ' '.join(lines)
                return docno, html_text
            lines.append(line.strip())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("raw_file_path")
    parser.add_argument("out_file_path")
    args = parser.parse_args()

    f_names = [args.raw_file_path]
    fout = open(args.out_file_path, 'w')

    cleanr = re.compile('<[^>]*>')
    for f_name in f_names:
        trec_reader = Reader(f_name)
        total_cnt = 0
        empty_cnt = 0
        err_cnt = 0

        for docno, html_text in trec_reader:
            total_cnt += 1

            if not html_text:
                empty_cnt += 1
                fout.write(docno + '\t' + '\n')
                continue

            try:
                extractor = Extractor(extractor='KeepEverythingExtractor', html=html_text)
                title = extractor.source.getTitle()
                body = extractor.getText()

                title = re.sub(cleanr, '', title)
                title = title.replace('\n', ' ').replace('\t', ' ')
                title = title.encode('ascii', 'ignore')

                body = re.sub(cleanr, '', body)
                body = body.replace('\n', ' ').replace('\t', ' ')
                body = body.encode('ascii', 'ignore')

                text = title + '\t' + body

                if text:
                    fout.write(docno + '\t' + text + '\n')
                else:
                    fout.write(docno + '\t' + '\n')
                    empty_cnt += 1
            except Exception as e:
                fout.write(docno + '\t' + '\n')
                err_cnt += 1

    fout.close()
    print empty_cnt, err_cnt

if __name__ == '__main__':
    main()
