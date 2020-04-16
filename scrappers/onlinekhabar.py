# -*- coding: utf-8 -*-

'''
    How to run:
        python scrapper.py \
            -n https://ekantipur.com \
            -s kantipur \
            -st 2020/04/10 \
            -et 2020/04/15
            
    Note:
        1. start_date should be less than end_date
                    
    To do:
        Add logger
        Add timer
'''

import re
import json
import sys
import os
import argparse

import urllib.request
from bs4 import BeautifulSoup
from urllib.parse import urlparse

import datetime
from datetime import date, timedelta


class ReadOnlyClass(type):
    def __setattr__(self, name, value):
        raise ValueError(name)


class Scrapper:
    __metaclass__ = ReadOnlyClass

    def __init__(self, news_link='', source='', given_date=''):
        self.NEWS_LINK = news_link
        self.SOURCE = source
        self.dump = {
            'news_link' : self.NEWS_LINK,
            'source' : self.SOURCE,
            'category' : {
            }
        }
        self.given_date = given_date
        self.published_date = ''
        
        if not os.path.exists(self.SOURCE):
            os.mkdir(self.SOURCE)
        
    def saveJson(self, directory=None, input_file=None):
        save_path = os.path.join(self.SOURCE, directory)
        
        if not os.path.exists(save_path):
            os.mkdir(save_path)
            
        filename = input_file + '.json'
        fname = os.path.join(save_path, filename)
        
        # Only write when file not present
        if not os.path.exists(fname):
            print("Dumping into file : {}".format(fname))
            with open(fname, 'w', encoding='utf-8') as f:
                json.dump(self.dump, f, ensure_ascii=False, indent=4)
            
    def getSoup(self, url=None):
        headers = {}
        headers['User-Agent'] ='Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
        req = urllib.request.Request(url, headers=headers)
        resp = urllib.request.urlopen(req).read()
        soup = BeautifulSoup(resp, 'html.parser')
        return soup
    
    def extractContent(self):
        soup = self.getSoup(self.NEWS_LINK+'/2020/04/')
        return self.parseContent(soup)

    def parseContent(self, content):
        self.extractCategory(content)

    def extractCategory(self, content):
        categoryOriginal = {}
        categories = {}
        
        # Content is None in last case
        try:
            for paragraph in content.find_all('a', href=True):
                link = paragraph.get('href')
                if link is not None and 'https' in link:
                    # This way we will get top headlines only
                    if paragraph.text == ' ':
                        break                    
                    categoryOriginal[link] = paragraph.text
                    
#             for k,v in categoryOriginal.items():
#                 print(k, v)
        except:
            print("Not found")
            
        self.extractHeadline(categoryOriginal)



    # retrieve headline for each category
    def extractHeadline(self, categoryList):

        for ind, (link, category) in enumerate(categoryList.items()):
            url = link
            
            # Get category name in English
            category_eng = url.split("/")[-1]
            
#             url += '/'+self.given_date
            url += '/page/1'
            soup = self.getSoup(url)
            
            headlineList = []
            for data in soup.find_all('a', href=True):
                link = str(data.get('href'))
                if link is not None:
                    try:
                        int(link[-1])
                        headlineList.append((category, link))
                        print(link)
                    except:
                        print("Not convertible")
            self.newsContents(headlineList)


    # retrieve the body for each headline
    def newsContents(self, headlineList):
        
        # Get the date wise dumps
#         date_dump = {}
#         for cat, each_link in headlineList:
#             curr_link = each_link.split('/')
#             current_date = curr_link[3]+curr_link[4]+curr_link[2] 
            
#             if current_date in date_dump:
#                 date_dump[current_date].append(each_link)
#             else:
#                 date_dump[current_date] = [each_link]
            
        # Get content date-wise
        # And store accordingly
#         for (key_date, list_value) in date_dump.items():
        news_dump = {}
        for index, (category, link) in enumerate(headlineList):
            print ("*************** Category : {}, #: {} ********************".format(category, (index + 1)))
            url = link
            # [1:] because of extra / in half_link
#             url = url.join((self.NEWS_LINK, half_link[1:]))
            print("Link :", url)

#             r = urllib.request.urlopen(url).read()
#             soup = BeautifulSoup(r, 'html.parser')
            
            soup = self.getSoup(url)

            title_source = soup.findAll('main', {'class': 'site-main'})
            news_title = ''
            for title in title_source:
                if title.find('h2') is not None:
                    news_title = title.find('h2').text
                    break
            
            print(news_title)
            
            nep_date = soup.find('div',{'class': ['post__time']}).text  
            nep_date = ' '.join(nep_date.split()[:-2])
            print(nep_date)
            
            try:
                author = soup.find('div',{'class': ['author__wrap']}).text  
            except:
                author = 'onlinekhabar'
            
            # Get only the content from 
            # normal article of main page of each link
            body_content = soup.find('div', {'class': ['col colspan3 main__read--content ok18-single-post-content-wrap']})

            news_body=' '

            # Some of the category has no content 
            # like photo_feature or video
            if body_content:
                for body in body_content.findAll('p'):
                    # check if it the body is empty
                    # exclude the javascript inside <p></p> tag
                    # exclude the duplicates from appending
                    if str(body.text.encode('ascii', 'ignore'))!="" \
                                    and 'script' not in str(body) \
                                    and body.text not in news_body:
                        news_body += body.text 
                
                # Get date
                split_url = url.split('/')
                print(split_url)
                cat_eng = split_url[-5]
                yy = split_url[-4]
                mm = split_url[-3]
                dd = split_url[-2]
                self.published_date = mm+dd+yy

                result = {
                    'cat_nep' : category,
                    'eng_date' : self.published_date,
                    'nep_date' : nep_date,
                    'author': author,
                    'title' : news_title,
                    'text' : news_body,
                    'url' : url
                }

                news_dump[str(index)] = result

        if len(news_dump) > 0:
            self.dump['category'] = news_dump
            self.saveJson(directory=category, input_file=key_date)                 
                

def main():
    parser = argparse.ArgumentParser("Kantipur Scrapper")
    parser.add_argument("-n", "--news_link", 
                        default="https://ekantipur.com/", 
                        metavar="LINK", help="News Link")
    parser.add_argument("-s", "--source", 
                        default="kantipur", 
                        metavar="SOURCE", help="News source name")
    parser.add_argument("-st", "--start_date", default="",
                        metavar="DATE", help="Date")
    parser.add_argument("-et", "--end_date", default="",
                        metavar="DATE", help="Date")    
    
    args = parser.parse_args()
    
    news_link = args.news_link
    news_source_name = args.source
    start_date = args.start_date
    end_date = args.end_date
    
    syear, smonth, sday = map(int, start_date.split('/'))
    sdate = datetime.date(syear, smonth, sday)
    
    eyear, emonth, eday = map(int, end_date.split('/'))
    edate = datetime.date(eyear, emonth, eday)
    
    delta = edate - sdate       # as timedelta

    for i in range(delta.days + 1):
        day = sdate + timedelta(days=i)
        given_date = day.strftime("%Y/%m/%d")
        print("Getting all the articles for :", given_date)
        scrappy = Scrapper(news_link=news_link, source=news_source_name, given_date=given_date)
        scrappy.extractContent()

if __name__ == '__main__':
    main()
