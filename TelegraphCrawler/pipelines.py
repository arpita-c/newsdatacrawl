# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import time;  # This is required to include time module
import os
import sys
import getopt
import datetime as dt
import MySQLdb
import requests
from lxml import html
from BeautifulSoup import BeautifulSoup 
import json
from unidecode import unidecode
from pymongo import MongoClient
import datetime


class TelegraphcrawlerPipeline(object):
    
    def __init__(self):
        #self.file = open('items.jl', 'wb')
        self.basepath="/home/arpita/WebCrawler/"
        self.topicdict={}
        self.client = MongoClient()
        #self.db = self.client.TelegraphData
        #Add New DB
        self.db = self.client.TelegraphData_August_Test
        #self.count=0;

    def getDateObject(self,datetime):
        print datetime
        datetimetokens=datetime.split(',')
        monthdatetoken=str(datetimetokens[1]).strip()

        monthdatetokenSpaceCut=monthdatetoken.replace(' ','')
        monthdatetokenSpaceCutDigitCount=self.hasNumbers(monthdatetokenSpaceCut)
        yeartoken=str(datetimetokens[2]).strip()
        #teo digit day is considered from 10th to 31st
        if (monthdatetokenSpaceCutDigitCount==2):
            month=monthdatetokenSpaceCut[:-2]
            day=monthdatetokenSpaceCut[-2:]
        elif(monthdatetokenSpaceCutDigitCount==1):
            month=monthdatetokenSpaceCut[:-1]
            day=monthdatetokenSpaceCut[-1:]

        datestring=month+" "+day+" "+yeartoken
        datestring=datestring.encode("utf-8")
        #print datestring
        from datetime import datetime
        date_object = datetime.strptime(datestring, '%B %d %Y')
        return date_object

    def hasNumbers(self,inputString):
        numbers = sum(c.isdigit() for c in inputString)
        return numbers

    def insertIntoDb(self,topicdict,topicname,story):
        storyheadline=story['headline']
        url=story['url']
        url=url.encode("utf-8")
        headline=storyheadline.encode("utf-8")
        content=unidecode(story['content'])
        category=topicname
        datetime=story['datetime']
        date_object=self.getDateObject(datetime)
        post={"Date":date_object,
          "Headline":headline,
          "Content":content,
          "Category":category,
          "weblink":url}

        tablename=topicname+"Data"
        #insert data to topic related table
        tableref = self.db[''+tablename+'']
        result=tableref.insert(post)
        #insert data to master table
        mastertableref=self.db['master']
        result=mastertableref.insert(post)
        #self.count=self.count+1
        #filename=self.basepath+"Count.rtf"

        #create a file pointer
        #fp=open(filename,"w")
        #fp.write("Total Count::"+str(self.count))
        #fp.close()


    def writeToFile(self,topicdict,topicname,story):
        #topicdict[topicname]
        
        url=story['url']
        headline=story['headline']
        datetime=story['datetime']
        content=unidecode(story['content'])    
        filetobewritten=topicdict[topicname]['filename']
        filereference=topicdict[topicname]['filepointer']
        filereference.write("\n \n ")
        filereference.write(headline.encode("utf-8"))
        filereference.write("\n \n ")
        filereference.write(datetime.encode("utf-8"))
        filereference.write("\n \n \n \n")
        filereference.write(content)
        filereference.write("\n \n ")
        filereference.write(url.encode("utf-8"))
        filereference.write("\n \n ")
            
                 
    #def open_spider(self, spider):
        #datestring=time.strftime("%d-%m-%Y")
        #self.resultfoldername="CrawlResult_"+datestring
        #self.resultfolder_full_path_directory=self.basepath+self.resultfoldername
        #if not os.path.exists(self.resultfolder_full_path_directory):
            #os.makedirs(self.resultfolder_full_path_directory)
            
    def createfolder(self, monthdatetokenSpaceCut,yeartoken):
        #datestring=time.strftime("%d-%m-%Y")
        self.resultfoldername="CrawlResult_"+monthdatetokenSpaceCut+"_"+yeartoken
        self.resultfolder_full_path_directory=self.basepath+self.resultfoldername
        if not os.path.exists(self.resultfolder_full_path_directory):
            os.makedirs(self.resultfolder_full_path_directory)            

    def process_item(self, item, spider):
        #print item
        story=item
        url=story['url']
        datetime=story['datetime']
        datetimetokens=datetime.split(',')
        monthdatetoken=str(datetimetokens[1]).strip()
        monthdatetokenSpaceCut=monthdatetoken.replace(' ','')
        yeartoken=str(datetimetokens[2]).strip()
        self.createfolder(monthdatetokenSpaceCut,yeartoken)
        
        #Split the url and get the topic name
        urlsplittedarray=url.split("/")
        urlsplittedarraylength=len(urlsplittedarray)
        topicname=urlsplittedarray[urlsplittedarraylength-2]
        
        
        
        if topicname not in self.topicdict:
            filename=topicname+".rtf"
            topicfilenamepath=self.resultfolder_full_path_directory+"/"+filename
        
            directory = os.path.dirname(topicfilenamepath)            
            if not os.path.exists(directory):
                os.makedirs(directory)
        
            # Open a file
            fo = open(topicfilenamepath, "w")            
            self.topicdict[topicname]={}
            self.topicdict[topicname]['filename']=topicfilenamepath
            self.topicdict[topicname]['filepointer']=fo
            self.writeToFile(self.topicdict,topicname,story)
            self.insertIntoDb(self.topicdict,topicname,story)
        else:
            self.writeToFile(self.topicdict,topicname,story)
            self.insertIntoDb(self.topicdict,topicname,story)
        return item     
    
    def close_spider(self, spider):


        for key in self.topicdict:
            #Get the file pointer
            filepointer=self.topicdict[key]['filepointer']
            filepointer.close()
        self.client.close()
