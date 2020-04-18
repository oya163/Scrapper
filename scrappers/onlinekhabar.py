# -*- coding: utf-8 -*-

'''
    How to run:
        python scrapper.py \
            -n https://ekantipur.com \
            -s kantipur \
            -p 15
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
from datetime import date, timedelta, time
import time
from nepali_date import NepaliDate

import logging
import logging.config

logname = 'onlinekhabar'
logger = logging.getLogger(logname)

data_path="./logs"
log_path = os.path.join(data_path, logname+".log")
logging.basicConfig(filename=log_path,level=logging.INFO,filemode='w')

formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')

sh = logging.StreamHandler(sys.stdout)
sh.setFormatter(formatter)
logger.addHandler(sh)

fh = logging.FileHandler(log_path)
fh.setFormatter(formatter)
logger.addHandler(fh)


class ReadOnlyClass(type):
    def __setattr__(self, name, value):
        raise ValueError(name)


class Scrapper:
    __metaclass__ = ReadOnlyClass

    def __init__(self, news_link='', source='', given_date='', page_num=''):
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
        self.page_num = page_num
        
        if not os.path.exists(self.SOURCE):
            os.mkdir(self.SOURCE)
            
        self.month_mapping = {'बैशाख':'1', 'वैशाख': '1', 
                              'जेष्ठ':'2','जेठ':'2',
                              'आषाढ':'3','असार':'3',
                              'श्रावण':'4','साउन':'4', 
                              'भाद्र':'5', 'भदौ':'5',
                              'आश्विन':'6', 'असोज':'6',
                              'कार्तिक':'7',
                              'मंसिर:':'8', 'मार्ग':'8',
                              'पौष':'9', 'पुष' :'9', 'पूस':'9',
                              'माघ':'10', 
                              'फाल्गुन':'11', 'फागुन':'11',
                              'चैत्र':'12', 'चैत':'12'}
        
        self.cat_map = {'समाचार':'news', 'विजनेश': 'business', 'जीवनशैली':'lifestyle','सूचना प्रविधि':'technology',
                       'मनोरन्जन':'entertainment', 'प्रवास': 'prabhas-news', 'खेलकुद':'sports', 'विविध': 'various',
                       'मनोरञ्जन':'entertainment'}
        
        
    def getDate(self, input_nep_date):
        nep_date = input_nep_date.split()
        yy = nep_date[0]
        mm = nep_date[1]
        dd = nep_date[2]
        nep_date = yy+'/'+self.month_mapping[mm]+'/'+dd
        nep_date = NepaliDate.strpdate(nep_date, '%Y/%m/%d')
        eng_date = nep_date.to_english_date().strftime('%m/%d/%Y')
        nep_date = nep_date.strfdate('%Y/%m/%d')
        return (nep_date, eng_date)
        
        
    def getEnglishCategory(self, text):
        return text
        
        
    def saveJson(self, directory=None, input_file=None):
        save_path = os.path.join(self.SOURCE, directory)

        if not os.path.exists(save_path):
            os.mkdir(save_path)
            
        filename = input_file + '.json'
        fname = os.path.join(save_path, filename)

        logger.info("Dumping into file : {}".format(fname))
        with open(fname, 'w', encoding='utf-8') as f:
            json.dump(self.dump, f, ensure_ascii=False, indent=4)
            
    # Return response of given url
    def getSoup(self, url=None):
        headers = {}
        headers['User-Agent'] ='Mozilla/5.0 (Windows NT 10.0; WOW64) \
                                AppleWebKit/537.36 (KHTML, like Gecko) \
                                Chrome/57.0.2987.133 Safari/537.36'
        req = urllib.request.Request(url, headers=headers)
        resp = urllib.request.urlopen(req).read()
        soup = BeautifulSoup(resp, 'html.parser')
        return soup
    
    # Return extracted content
    def extractContent(self):
        soup = self.getSoup(self.NEWS_LINK)
        return self.extractCategory(soup)
        
    # Create dictionary of all categories
    def extractCategory(self, content):
        categories = {}
        
        # Get all the topics and subtopics
        # mentioned in footer of main page
        for footer in content.find_all('div', {'class':'seven__cols--grid footer__grid'}):
            # Exclude the first item
            for elm in footer.select(".col")[1:]:
                topic = elm.find('h2').get_text()
                items = elm.find_all('a', href=True)
                for each in items:
                    half_link = each.get('href')
                    subtopic_eng = half_link.split("/")[-1] if half_link.split("/")[-1] else half_link.split("/")[-2]
                    subtopic_nep = each.get_text()
                    subtopic = (subtopic_eng, subtopic_nep)
                    categories[half_link] = (self.cat_map[topic], topic, subtopic)

#         logger.info("All the available categories")
#         for k,v in categories.items():
#             logger.info("{},{}".format(k, v))
            
        self.extractNewHeadline(categories) 
        

    # retrieve link for each category
    def extractNewHeadline(self, categoryDict):
        # Create a complete ArticleID based dictionary
        articleIdDict = {}
        
        # Iterate through each category
        for i in range(0, self.page_num):
            page_num = i+1
            suffix = '/page/'+str(page_num)
            for link, (topic, cat_nep, subtopic) in categoryDict.items():    
                url = ''.join((self.NEWS_LINK, link+suffix))
                if 'contact-us' not in url:
                    logger.info("Getting all contents from {}".format(url))
                    
                    soup = self.getSoup(url)
                    
                    for data in soup.find_all('a', href=True):
                        link = str(data.get('href'))
                        if link and 'trend' not in link and 'content' not in link \
                                and 'www.onlinekhabar.com' in link \
                                and '2020' in link:
                            article_id = link.split("/")[-1]
                            if article_id not in articleIdDict:
                                articleIdDict[article_id] = ((page_num, topic, cat_nep, subtopic, link))
                                logger.info("Page Num:{} Topic:{} SubTopic:{} Link:{}".format(page_num, topic, subtopic, link))
#                             else:
#                                 logger.info("Reporting duplicates : {}".format(link))
                        
#         print("All the available items")
#         for k,v in articleIdDict.items():
#             logger.info("{},{}".format(k, v))

        self.newsNewContents(articleIdDict)
            

    # retrieve the body for each headline
    def newsNewContents(self, articleIdDict):
        # Get the date wise dumps
        date_dump = {}
        for (article_id), (pg_num, topic, cat_nep, subtopic, each_link) in articleIdDict.items():
            curr_link = each_link.split('/')
            current_date = curr_link[-2]+curr_link[-3]
            
            value = (pg_num, article_id, topic, cat_nep, subtopic, each_link)
            if current_date in date_dump:
                date_dump[current_date].append(value)
            else:
                date_dump[current_date] = [value]
        
        # Sort right here !!!
#         logger.info("All the available items")
#         for key_date,list_value in sorted(date_dump.items()):
#             list_value = sorted(list_value, key = lambda x: x[2])
#             for each in list_value:
#                 logger.info("{},{}".format(key_date, each))
            
#         sys.exit(00)
        
        # Iterate through each date
        for (key_date, list_value) in sorted(date_dump.items()):
            # Sort by the topic
            list_value = sorted(list_value, key = lambda x: x[2])
            
            # Dictionary of news_dump
            news_dump = {}
            
            # Prev category
            prev_cat = list_value[0][2]
            
            # Iterate through each articles
            for index, (pg_num, article_id, topic, cat_nep, (subtopic_eng, subtopic_nep), link) in enumerate(list_value):
                logger.info ("***************Page Num:{} Category:{}, SubCategory:{}, Index: {} ********************".format(pg_num, topic, subtopic_eng, (index + 1)))
                url = link
                logger.info("Link : {}".format(url))

                soup = self.getSoup(url)

                title_source = soup.findAll('main', {'class': 'site-main'})
                news_title = ''
                for title in title_source:
                    if title.find('h2') is not None:
                        news_title = title.find('h2').text
                        break

                logger.info("Title : {}".format(news_title))

                nep_date = soup.find('div',{'class': ['post__time']}).text  
                nep_date = ' '.join(nep_date.split()[:-2])

                author = soup.find('div',{'class': ['author__wrap']}).text.replace('\n','')

                # Get only the content from 
                # normal article of main page of each link
                body_content = soup.find('div', {'class': ['col colspan3 main__read--content ok18-single-post-content-wrap']})

                news_body=' '

                # Some of the category has no content 
                # like photo_feature or video
                for body in body_content.findAll('p'):
                    # check if it the body is empty
                    # exclude the javascript inside <p></p> tag
                    # exclude the duplicates from appending
                    if str(body.text.encode('ascii', 'ignore'))!="" \
                                    and 'script' not in str(body) \
                                    and body.text not in news_body:
                        news_body += body.text 

                # Get dates in proper format
                nep_date, eng_date = self.getDate(nep_date)

                # Get category in English
                cat_eng = topic

                result = {
                    'article_id' : article_id,
                    'cat_nep' : cat_nep,
                    'cat_eng' : cat_eng,
                    'subcat_eng' : subtopic_eng,
                    'subcat_nep' : subtopic_nep,
                    'eng_date' : eng_date,
                    'nep_date' : nep_date,
                    'author': author,
                    'title' : news_title,
                    'text' : news_body,
                    'url' : url
                }
                
                
                # Save it if the previous category is not
                # same as current category
                if prev_cat != cat_eng:
                    self.dump['category'] = news_dump
                    logger.info("Length of news dump in {} category : {}".format(prev_cat, len(news_dump)))
                    self.saveJson(directory=prev_cat, input_file=key_date)
                    news_dump={}
                    prev_cat = cat_eng
                    
                news_dump[article_id] = result
                
            # Saving last category            
            self.dump['category'] = news_dump
            logger.info("Length of news dump in {} category : {}".format(prev_cat, len(news_dump)))
            self.saveJson(directory=prev_cat, input_file=key_date)


def main():
    parser = argparse.ArgumentParser("Online Khabar Scrapper")
    parser.add_argument("-n", "--news_link", 
                        default="https://www.onlinekhabar.com", 
                        metavar="LINK", help="News Link")
    parser.add_argument("-s", "--source", 
                        default="onlinekhabar", 
                        metavar="SOURCE", help="News source name")
    parser.add_argument("-d", "--given_date", default=None,
                        metavar="DATE", help="Date Format : 2020/04")
    parser.add_argument("-p", "--page_num", default=10, type=int,
                        metavar="PAGE", help="Number of pages to scrap")    
    
    args = parser.parse_args()
    
    news_link = args.news_link
    news_source_name = args.source
    page_num = args.page_num
    # Take today's date if not given on arguments
    given_date = args.given_date if args.given_date else date.today().strftime("%Y/%m")
    
    logger.info("Scrapping at least {} pages from each categories ahead of {} date".format(page_num, given_date))
    
    start_time = time.time()
    scrappy = Scrapper(news_link=news_link, source=news_source_name, given_date=given_date, page_num=page_num)
    scrappy.extractContent()
    seconds = time.time() - start_time
    
    logger.info("Total time taken to scrap : {}".format(time.strftime("%H:%M:%S",time.gmtime(seconds))))

if __name__ == '__main__':
    main()
