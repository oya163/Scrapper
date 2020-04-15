# -*- coding: utf-8 -*-

import re
import json
import sys
import os
import argparse

import urllib.request
from bs4 import BeautifulSoup
from urllib.parse import urlparse


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
            print("Saving file : ", fname)
            with open(fname, 'w', encoding='utf-8') as f:
                json.dump(self.dump, f, ensure_ascii=False, indent=4)
            

    def extractContent(self):
        r = urllib.request.urlopen(self.NEWS_LINK).read()
        soup = BeautifulSoup(r, 'html.parser')
        return self.parseContent(soup)

    def parseContent(self, content):
        self.extractCategory(content)

    def extractCategory(self, content):
        categoryOriginal = {}
        categories = {}

        for paragraph in content.find_all('a'):
            link = paragraph.get('href')
            
            if link is not None and 'https' in link:
                # To get all the main title page
                # There is break in paragraph text
                if paragraph.text == '':
                    break
                categoryOriginal[paragraph.get('href')] = paragraph.text

        self.extractHeadline(categoryOriginal)


    # retrieve headline for each category
    def extractHeadline(self, categoryList):

        for ind, (link, category) in enumerate(categoryList.items()):
            url = link
            
            # Get category name in English
            category_eng = url.split("/")[-1]
            
            url += '/'+self.given_date
            
            r = urllib.request.urlopen(url).read()
            soup = BeautifulSoup(r, 'html.parser')

            headlineList = []
            for data in soup.find_all('div', {'class': ['teaser offset']}):
                if data.find('a') is not None:
                    # verify that it is content page
                    if 'html' in data.find('a').get('href'):
                        headlineList.append((category, data.find('a').get('href')))
                
            self.newsContents(headlineList)


    # retrieve the body for each headline
    def newsContents(self, headlineList):
        
        # Get the date wise dumps
        date_dump = {}
        for cat, each_link in headlineList:
            curr_link = each_link.split('/')
            current_date = curr_link[3]+curr_link[4]+curr_link[2] 
            
            if current_date in date_dump:
                date_dump[current_date].append(each_link)
            else:
                date_dump[current_date] = [each_link]
            
        # Get content date-wise
        # And store accordingly
        for (key_date, list_value) in date_dump.items():
            news_dump = {}
            for index, half_link in enumerate(list_value):
                category = half_link.split('/')[1]
                print ("*************** Category : {}, #: {} ********************".format(category, (index + 1)))
                url = ''
                
                # [1:] because of extra / in half_link
                url = url.join((self.NEWS_LINK, half_link[1:]))
                print("Link :", url)

                r = urllib.request.urlopen(url).read()
                soup = BeautifulSoup(r, 'html.parser')

                title_source = soup.find_all('div', {'class': ['article-header']})
                if title_source[0].find({'h1', 'h2'}) is not None:
                    news_title = title_source[0].find({'h1', 'h2'}).text

                author = soup.find('span',{'class': ['author']}).text
                nep_date = soup.find('time',{'style': ['display:inline-block']}).text           

                # Get only the content from 
                # normal article of main page of each link
                body_content = soup.find('article', {'class': ['normal']})

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

                    # To remove unnecessary end of the sentence
                    # For example - प्रकाशित : वैशाख ३, २०७७ ०८:२७
                    news_body = ' '.join(news_body.split()[:-6])

                    # Get date
                    split_url = url.split('/')
                    cat_eng = split_url[-5]
                    yy = split_url[-4]
                    mm = split_url[-3]
                    dd = split_url[-2]
                    self.published_date = mm+dd+yy

                    result = {
                        'cat_eng' : cat_eng,
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
                print("Saving JSON file !!!")
                self.saveJson(directory=category, input_file=key_date)                 
                

def main():
    parser = argparse.ArgumentParser("Kantipur Scrapper")
    parser.add_argument("-n", "--news_link", 
                        default="https://ekantipur.com/", 
                        metavar="LINK", help="News Link")
    parser.add_argument("-s", "--news_source_name", 
                        default="kantipur", 
                        metavar="SOURCE", help="News source name")
    parser.add_argument("-d", "--date", default="",
                        metavar="DATE", help="Date")
    
    args = parser.parse_args()
    
    news_link = args.news_link
    news_source_name = args.news_source_name
    date = args.date
    
    scrappy = Scrapper(news_link=news_link, source=news_source_name, given_date=date)
    scrappy.extractContent()

if __name__ == '__main__':
    main()
