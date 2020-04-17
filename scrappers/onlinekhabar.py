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
from datetime import date, timedelta, time
from nepali_date import NepaliDate

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
            
        self.month_mapping = {'बैशाख':'1', 'वैशाख': '1', 
                              'जेष्ठ':'2','जेठ':'2',
                              'आषाढ':'3','असार':'3',
                              'श्रावण':'4','साउन':'4', 
                              'भाद्र':'5', 'भदौ':'5',
                              'आश्विन':'6', 'असोज':'6',
                              'कार्तिक':'7',
                              'मार्ग':'8', 'मंसिर:':'8',
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

        print("Dumping into file : {}".format(fname))
        with open(fname, 'w', encoding='utf-8') as f:
            json.dump(self.dump, f, ensure_ascii=False, indent=4)
            
    def getSoup(self, url=None):
        headers = {}
        headers['User-Agent'] ='Mozilla/5.0 (Windows NT 10.0; WOW64) \
                                AppleWebKit/537.36 (KHTML, like Gecko) \
                                Chrome/57.0.2987.133 Safari/537.36'
        req = urllib.request.Request(url, headers=headers)
        resp = urllib.request.urlopen(req).read()
        soup = BeautifulSoup(resp, 'html.parser')
        return soup
    
    def extractContent(self):
        soup = self.getSoup(self.NEWS_LINK)
        return self.parseContent(soup)

    def parseContent(self, content):
        self.extractCategory(content)
        
    def extractCategory(self, content):
        categories = {}
        
        # Content is None in last case
        for footer in content.find_all('div', {'class':'seven__cols--grid footer__grid'}):
            # Exclude the first item
            for elm in footer.select(".col")[1:]:
                topic = elm.find('h2').get_text()
                print(topic)
                items = elm.find_all('a', href=True)
                for each in items:
                    half_link = each.get('href')
                    subtopic = each.get_text()

                    categories[half_link] = (self.cat_map[topic], subtopic)

        print("All the available categories")
        for k,v in categories.items():
            print(k, v)

        # Get all subcategories
        
        sys.exit(00)
            
        self.extractNewHeadline(categories) 

    # retrieve headline for each category
    def extractNewHeadline(self, categoryDict):
        # Crawl through each page here
        # Create list of links of each page
        # Pass it to newsContents function
        # Dump it to file category wise        
        articleIdDict = {}
        for link, (topic, subtopic) in categoryDict.items():
            url = ''.join((self.NEWS_LINK, link))
            print(url, topic)
            
            soup = self.getSoup(url)
            
            for data in soup.find_all('a', href=True):
                link = str(data.get('href'))
                if link and 'trend' not in link and 'content' not in link and 'www.onlinekhabar.com' in link:
                    article_id = link.split("/")[-1]
                    if article_id not in articleIdDict:
                        articleIdDict[article_id] = ((topic,subtopic,link))
                        print(topic,subtopic,link)
                    else:
                        print("Reporting duplicate ID ", article_id)
#                         print("Reporting duplicate LINK ", link)
                        
#             print("All the available categories")
#             for k,v in articleIdDict.items():
#                 print(k, v)
                
        self.newsNewContents(articleIdDict)

    # retrieve the body for each headline
    def newsNewContents(self, articleIdDict):
        # Get the date wise dumps
        date_dump = {}
        for article_id, (topic, subtopic, each_link) in articleIdDict.items():
            curr_link = each_link.split('/')
            current_date = curr_link[-2]+curr_link[-3]
            
            value = (article_id, topic, subtopic, each_link)
            if current_date in date_dump:
                date_dump[current_date].append(value)
            else:
                date_dump[current_date] = [value]
        
        # Get the date wise dumps
        news_dump = {}
        for (key_date, list_value) in date_dump.items():
            for index, (article_id, category, subtopic, each_link) in enumerate(list_value):
                category = topic
                print ("*************** Category : {}, Index: {} ********************".format(category, (index + 1)))
                url = link
                article_id = link.split('/')[-1]
                print("Link :", url)

                soup = self.getSoup(url)

                title_source = soup.findAll('main', {'class': 'site-main'})
                news_title = ''
                for title in title_source:
                    if title.find('h2') is not None:
                        news_title = title.find('h2').text
                        break

                print("Title : ", news_title)

                nep_date = soup.find('div',{'class': ['post__time']}).text  
                nep_date = ' '.join(nep_date.split()[:-2])

                try:
                    author = soup.find('div',{'class': ['author__wrap']}).text.replace('\n','')  
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
                    nep_date, eng_date = self.getDate(nep_date)

                    cat_eng = self.cat_map[category]

                    result = {
                        'article_id' : article_id,
                        'cat_nep' : category,
                        'cat_eng' : cat_eng,
                        'eng_date' : eng_date,
                        'nep_date' : nep_date,
                        'author': author,
                        'title' : news_title,
                        'text' : news_body,
                        'url' : url
                    }
                    news_dump[article_id] = result

#             for k,v in news_dump.items():
#                 print(k, v['url'], v['title'])                

            self.dump['category'] = news_dump
            print("Length of news dump in this category = ", len(news_dump))
            self.saveJson(directory=cat_eng, input_file=key_date)              

    # retrieve headline for each category
    def extractHeadline(self, categoryList):
        # Make a global dict of all article_id
        # So it does not repeat accessing the articles again
        for ind, (link, category) in enumerate(categoryList.items()):
            articleIdSet = set()
            # I just gave randomly 40
            # to download 40 pages of every category
            for i in range(1,30):
                url = link

                # Get category name in English
                category_eng = url.split("/")[-1]

                url += 'page/'+str(i)
                try:
                    soup = self.getSoup(url)
                except:
                    print("Unknown url")

                headlineList = []
                try:
                    for data in soup.find_all('a', href=True):
                        link = str(data.get('href'))
                        # Removing trending link as well
                        # Remove those last links having page 2/ or 3/ or 7625/
                        # Remove those links outside of onlinekhabar
                        if link is not None and 'trend' not in link and 'www.onlinekhabar.com' in link:
                            # online khabar valid website has last
                            # character as integer on every link
                            try:
                                int(link[-1])
                                # Create article_id dictionary
                                # to stop repeating the articles
                                article_id = link.split("/")[-1]
                                if article_id not in articleIdSet:
                                    articleIdSet.add(article_id)
                                    headlineList.append((category, link))
                                    print("LINK = ", link)
                                else:
                                    print("Duplicate = ", link)
                            except:
                                print("Not convertible")
                except:
                    print("Unknown link")

                self.newsContents(headlineList)


    # retrieve the body for each headline
    def newsContents(self, articleIdDict):
        # Get the date wise dumps
        date_dump = {}
        for cat, each_link in headlineList:
            curr_link = each_link.split('/')
            current_date = curr_link[-2]+curr_link[-3]
            
            value = (cat, each_link)
            if current_date in date_dump:
                date_dump[current_date].append(value)
            else:
                date_dump[current_date] = [value]

        # Get the date wise dumps
        news_dump = {}
        for (key_date, list_value) in date_dump.items():
            for index, (category, link) in enumerate(list_value):
                print ("*************** Category : {}, Index: {} ********************".format(category, (index + 1)))
                url = link
                article_id = link.split('/')[-1]
                print("Link :", url)

                soup = self.getSoup(url)

                title_source = soup.findAll('main', {'class': 'site-main'})
                news_title = ''
                for title in title_source:
                    if title.find('h2') is not None:
                        news_title = title.find('h2').text
                        break

                print("Title : ", news_title)

                nep_date = soup.find('div',{'class': ['post__time']}).text  
                nep_date = ' '.join(nep_date.split()[:-2])

                try:
                    author = soup.find('div',{'class': ['author__wrap']}).text.replace('\n','')  
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
                    nep_date, eng_date = self.getDate(nep_date)

                    cat_eng = self.cat_map[category]

                    result = {
                        'article_id' : article_id,
                        'cat_nep' : category,
                        'cat_eng' : cat_eng,
                        'eng_date' : eng_date,
                        'nep_date' : nep_date,
                        'author': author,
                        'title' : news_title,
                        'text' : news_body,
                        'url' : url
                    }
                    news_dump[article_id] = result

#             for k,v in news_dump.items():
#                 print(k, v['url'], v['title'])                

            self.dump['category'] = news_dump
            print("Length of news dump in this category = ", len(news_dump))
            self.saveJson(directory=cat_eng, input_file=key_date)               
                

def main():
    parser = argparse.ArgumentParser("Online Khabar Scrapper")
    parser.add_argument("-n", "--news_link", 
                        default="https://www.onlinekhabar.com", 
                        metavar="LINK", help="News Link")
    parser.add_argument("-s", "--source", 
                        default="onlinekhabar", 
                        metavar="SOURCE", help="News source name")
    parser.add_argument("-d", "--given_date", default="2020/04",
                        metavar="DATE", help="Date")
    parser.add_argument("-et", "--end_date", default="2020/04/17",
                        metavar="DATE", help="Date")    
    
    args = parser.parse_args()
    
    news_link = args.news_link
    news_source_name = args.source
    
    # Fix current date if not given
    given_date = args.given_date
    
    print("Getting all the articles for :", given_date)
    scrappy = Scrapper(news_link=news_link, source=news_source_name, given_date=given_date)
    scrappy.extractContent()

if __name__ == '__main__':
    main()
