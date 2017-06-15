#!/usr/bin/python  
#-*- coding: utf-8 -*-
#
# Create by Meibenjin. 
#
# Last updated: 2013-04-02
#
# google search results crawler 

import sys
import json
reload(sys)
sys.setdefaultencoding('utf-8')

import urllib2, socket, time
import gzip, StringIO
import re, random, types
import argparse

from bs4 import BeautifulSoup 

base_url = 'https://www.google.com/'
results_per_page = 10

user_agents = list()
bad_agents = set()

# results from the search engine
# basically include url, title,content
class SearchResult:
    def __init__(self):
        self.url= '' 
        self.title = '' 
        self.content = ''
        self.query = ''

    def getQuery(self):
        return self.query

    def setQuery(self, q):
        self.query = q

    def getURL(self):
        return self.url

    def setURL(self, url):
        self.url = url 

    def getTitle(self):
        return self.title

    def setTitle(self, title):
        self.title = self.cleanText(title)

    def getContent(self):
        return self.content

    def setContent(self, content):
        self.content = self.cleanText(content)

    def cleanText(self, text):
        cleantext = BeautifulSoup(text).text
        cleantext = cleantext.replace('\n', ' ')
        return cleantext

    def printIt(self, prefix = ''):
        print 'url\t', self.url
        print 'title\t', self.title
        print 'content\t', self.content
        print 

    def writeFile(self, filename):
        file = open(filename, 'a')
        try:
            file.write('url\t' + self.url+ '\n')
            file.write('title\t' + self.title + '\n')
            file.write('content\t' + self.content + '\n\n')

        except IOError, e:
            print 'file error:', e
        finally:
            file.close()

    def to_json_str(self):
        obj = {"query": self.query, "doc": {"url": self.url, "title": self.title, "snippet": self.content}}
        out_str = json.dumps(obj)
        return out_str


class GoogleAPI:
    def __init__(self):
        timeout = 40
        socket.setdefaulttimeout(timeout)

    def randomSleep(self, lb=60, up=120):
        sleeptime = random.randint(lb, up)
        time.sleep(sleeptime)

    #extract the domain of a url
    def extractDomain(self, url):
        domain = ''
        pattern = re.compile(r'http[s]?://([^/]+)/', re.U | re.M)
        url_match = pattern.search(url)
        if url_match and url_match.lastindex > 0:
            domain = url_match.group(1)

        return domain

    #extract a url from a link
    def extractUrl(self, href):
        url = ''
        pattern = re.compile(r'(http[s]?://[^&]+)&', re.U | re.M)
        url_match = pattern.search(href)
        if url_match and url_match.lastindex > 0:
            url = url_match.group(1)

        return url 

    # extract serach results list from downloaded html file
    def extractSearchResults(self, html):
        results = list()
        soup = BeautifulSoup(html)
        div = soup.find('div', id ='search')
        if div:
            lis = div.findAll('div', {'class': 'g'})
            if len(lis) == 0:
                lis = div.findAll('div', {'class': 'g'})
            if len(lis) > 0:
                for li in lis:
                    result = SearchResult()
                    h3 = li.find('h3', {'class': 'r'})
                    if not h3:
                        continue

                    # extract domain and title from h3 object
                    link = h3.find('a')
                    if not link:
                        continue

                    url = link['href']
                    url = self.extractUrl(url)
                    if cmp(url, '') == 0:
                        continue
                    title = link.renderContents()
                    result.setURL(url)
                    result.setTitle(title)

                    span = li.find('span', {'class': 'st'})
                    if span:
                        content = span.renderContents()
                        result.setContent(content)
                    results.append(result)
        return results

    # search web
    # @param query -> query key words 
    # @param lang -> language of search results  
    # @param num -> number of search results to return 
    def search(self, query, lang='en', num=results_per_page):
        self.randomSleep(0, 20)
        search_results = list()
        query = urllib2.quote(query)
        if num % results_per_page == 0:
            pages = num / results_per_page
        else:
            pages = num / results_per_page + 1

        for p in range(0, pages):
            start = p * results_per_page 
            url = '%s/search?hl=%s&num=%d&start=%s&q=%s' % (base_url, lang, results_per_page, start, query)
            print url
            retry = 3
            while(retry > 0):
                try:
                    request = urllib2.Request(url)
                    length = len(user_agents)
                    while True:
                        index = random.randint(0, length-1)
                        if index not in bad_agents:
                            break
                    user_agent = user_agents[index] 
                    request.add_header('User-agent', user_agent)
                    request.add_header('Accept-Encoding', 'gzip')
                    request.add_header('referer', base_url)
                    response = urllib2.urlopen(request)
                    html = response.read() 
                    if response.headers.get('content-encoding', None) == 'gzip':
                        html = gzip.GzipFile(fileobj=StringIO.StringIO(html)).read()

                    results = self.extractSearchResults(html)
                    if not results:
                        bad_agents.add(index)
                        print "bad agent: ", user_agents[index]
                    search_results.extend(results)
                    break
                except urllib2.URLError,e:
                    print 'url error:', e
                    self.randomSleep()
                    retry -= 1
                    continue
                
                except Exception, e:
                    print 'error:', e
                    retry -= 1
                    self.randomSleep()
                    continue
        return search_results 


def load_user_agent():
    fp = open('./data/user_agents', 'r')

    line = fp.readline().strip('\n')
    while(line):
        user_agents.append(line)
        line = fp.readline().strip('\n')
    fp.close()


def crawler(keyword_file, out_file):
    # Load use agent string from file
    load_user_agent()

    # Create a GoogleAPI instance
    api = GoogleAPI()

    # set expect search results to be crawled
    expect_num = 10
    # if no parameters, read query keywords from file

    keywords = open(keyword_file, 'r')
    outf = open(out_file, 'w')
    keyword = keywords.readline().strip()
    n_keywords = 0
    n_empty = 0
    while keyword:
        n_keywords += 1
        results = api.search(keyword, num=expect_num)
        if not results:
            n_empty += 1
            print keyword
        for r in results:
            r.setQuery(keyword)
            jstr = r.to_json_str()
            print >> outf, jstr
        if n_keywords % 10 == 0:
            print "{0} queries, {1} failed.".format(n_keywords, n_empty)
        keyword = keywords.readline().strip()
    keywords.close()
    out_file.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("query_file")
    parser.add_argument("out_file")
    args = parser.parse_args()
    crawler(args.query_file, args.out_file)
