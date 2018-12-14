import os
import sys
import getopt
import datetime as dt
import scrapy
from scrapy.spiders import Spider
from scrapy.spiders import BaseSpider 
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import Selector
from scrapy.selector import HtmlXPathSelector 
from scrapy.item import Item, Field
import urllib
import urlparse
from scrapy.http.request import Request
from scrapy.http.response import Response
from BeautifulSoup import BeautifulSoup 
import requests
import json
from TelegraphCrawler.items import ScrapyItem
from TelegraphCrawler.items import ScrapyItemDetails



class TelegraphSpider(scrapy.Spider):
    name = 'telegraphindia'
    #allowed_domains = ["telegraphindia.com"]
    #base_url="http://localhost:63342/static/TestInput"
    base_url="http://www.telegraphindia.com/"
    #start_urls = ["http://www.telegraphindia.com/"]
    
    #start_urls = ["http://localhost:63343/static/TestInput/The%20Telegraph%20ugust-%20Archives_01May007.html"]
    start_urls = ["http://localhost:63342/TelegraphCrawler/TestInput/August/The%20Telegraph%20-%20Archives_30AUGUST2015.html"]
    filename_url="http://localhost:63342/TelegraphCrawler/TestInput/August/The%20Telegraph%20-%20Archives_30AUGUST2015_files/"
    def parse(self,response):
        #for href in response.css('head link::attr(href)'):
        
        #url=response.url
        #print url
        #output = requests.get(url)
        #print output
        #response=output.encode("utf-8")
        sel = Selector(response)
        elments=sel.xpath('//frame[@name="mainFrame"]')
        urllist=elments.xpath('./@src').extract()
        url=''.join(urllist)
        if (url.startswith("http:")==True):
            full_url=url
        else:    
            url=url[2:]
            full_url="http://localhost:63342/TelegraphCrawler/TestInput/August/"+url
        #print full_url
        #yield Request(urlparse.urljoin(response.url, url),callback=self.parse_url)
        yield Request(full_url,callback=self.parse_url)
        #output=requests.get(full_url)
        #output=output.encode("utf-8")

    def parse_url(self,response):
        
        #print response.url
        #print response.url
        #print "Hi"
        #print response.url
        #print response.body
        sel = Selector(text=response.body)
        
        elments=sel.xpath('//a')
        
        #elems=response.css('body li a:: attr(href)')
        #results=[]
        news_topic_covered=["Front Page","Nation","Calcutta","Bengal","Foreign","Business","Sports","Horse Racing","t2","Opinion","Metro","North Bengal","Northeast","Jharkhand","Bihar","Odisha"]
        css_classes_ignored=["lead","secondLead","sectionHeading","more"]
        links = []
        fontpageflag=False
        for elem in elments:
            class_name=elem.xpath('./@class').extract()
            if class_name!=[]:
                continue

            caption=elem.xpath('./text()').extract()
            #print caption
            caption_string=''.join(caption)
            #print caption_string
            listflag=True
            if caption_string in news_topic_covered:
                
                elem_url=elem.xpath('./@href').extract()

                #if(caption_string=="Front Page"):
                    #print "Front PAge Link::"+''.join(  elem_url)
                relative_url=''.join(elem_url)
                full_url=self.base_url+relative_url

                if "http:" in relative_url:
                    full_url=relative_url
                else:
                    if relative_url=="index.html":
                        fontpageflag=True
                        listflag=False
                        #full_url=self.filename_url+relative_url
                        #full_url=response.url
                    else:    
                        full_url=self.base_url+relative_url
                if(listflag==True):
                    httpOutString=full_url[7:]
                    httpInString=full_url[:7]
                    httpOutString=httpOutString.replace("//","/")
                    full_url=httpInString+httpOutString
                    #print full_url
                    #relative_url_about=relative_url.split("/")[2]

                    links.append(full_url)
                #yield scrapy.Request(full_url, callback=self.parse_question)
            else:
                continue
        frontpage_url=""
        #print "Hi"+ str(fontpageflag)
        if fontpageflag==True:
            loopflag=False
            for link in links:
                val=link
                for number in val.split("/"):
                    if number.isdigit()==True:
                        #print number
                        frontpage_url="http://www.telegraphindia.com/"+str(number)+"/jsp/frontpage/index.jsp"
                        loopflag=True
                        break
                if(loopflag==True):
                    break
        #print str(len(frontpage_url))+"::"+str(fontpageflag)
        if len(frontpage_url)>1 and fontpageflag==True:
            links.append(frontpage_url)
        for link in links: 
            item=ScrapyItem() 
            item['link']=link
            print item['link']
            yield Request(item['link'], meta={'item':item},callback=self.parse_listing_page)
       
        
            #print item['childlink']
        #for href in response.css('body .nav nav-list .nav-header li a::attr(href)'):
            #full_url = response.urljoin(href.extract())
            #yield scrapy.Request(full_url, callback=self.parse_question)

    #scrap listing page to get content        
    def parse_listing_page(self, response):
        #print response.url
        hxs = Selector(response) 
        item = response.request.meta['item'] 
        #if(response.url=="http://localhost:63342/static/TestInput/The%20Telegraph%20-%20Archives_01MAY2007_files/index.html"):
            #print "Hi"
        #child_node_list = hxs.select('//table[@class="story-table"]')
        child_node_list=hxs.xpath('//a//@href')
        item['childlink']=[]
        #item['childlinkcontent']={}
        #print "Hello"
        for node in child_node_list:
            #nodedetailsurl=node.xpath('./tr//td//h2//a//@href').extract()
            nodedetailsurl=node.extract()
            #print nodedetailsurl
            if "story_" in nodedetailsurl:
            
                #datetime=node.xpath('./tr//td//abbr/text()').extract()
                lastindex=response.url.rfind("/")
                nodedetailsurl_string=response.url[:lastindex+1]+''.join(nodedetailsurl)
                #print nodedetailsurl_string
                if nodedetailsurl_string not in item['childlink']:
                    item['childlink'].append(nodedetailsurl_string)
                    yield Request(urlparse.urljoin(response.url, nodedetailsurl_string), meta={'item':item},callback=self.parse_listing_page_details)
                    
            else:
                continue
        #print "Dona"
        #self.extractDataFromJsonFile()
                
        #item['content'] = hxs.select('//..../text()').extract()[0] 
        #yield item        
        #yield {
            #'title': response.url
            
        #}
        
    #scrap listing page to get content details        
    def parse_listing_page_details(self, response):
        isSectionheadline=False
        hxs = Selector(response)
        item = response.request.meta['item']
        item['childlinkcontent']=ScrapyItemDetails()
        item['childlinkcontent']['url']=response.url;
        datetime = hxs.xpath('//span[@class="date"]/text()').extract()
        headline = hxs.xpath('//h1[@class="articleheader"]/text()').extract()
        #isSectionheadline=False

        if(headline==[]):
            headline = hxs.xpath('//h1[@class="sectionheading"]/text()').extract()
            if headline==[]:
                headline = hxs.xpath('//td[@class="sectionheading"]/text()').extract()
            isSectionheadline=True

        item['childlinkcontent']['headline']=''.join(headline)
        item['childlinkcontent']['datetime']=''.join(datetime)

        page = requests.get(item['childlinkcontent']['url'])

        #Craete a object of BeautifulSoup
        soup = BeautifulSoup(page.text)

        #structure the html by handling unclosed tag
        soup.prettify()
        eliminated_script_tag=False
        if (isSectionheadline==False):
            contentnodelist=soup.findAll('p')
            content=""
            eliminated_script_tag=False
            for contentnode in contentnodelist:
                    #print hit
                
                if((contentnode.get('class') is not None) and ((contentnode.get('class').strip())=="storyBold")):
                    continue
                if((contentnode.get('class') is not None) and ((contentnode.get('class').strip())=="caption")):
                    continue
                
                
                #if(contentnode.get('class')=="storyBold"):
                    #continue
                #if(contentnode.get('class')=="caption"):
                    #continue
                
                #eliminated_script_tag=False
                #get children of contentnode
                children = contentnode.findChildren()
                eliminated_script_tag=False
                for child in children:
                    if(child.name=="script"):
                        eliminated_script_tag=True
                        #Get the eliminated _script_tag string
                        print "Hello"
                        eliminated_string=child.string
                        print eliminated_string
                
                 
                content=content+" "+' '.join( contentnode.findAll(text=True, recursive=True))
                if(eliminated_script_tag==True):
                    content=content.replace(eliminated_string," ")
                
                #replace &quote token with ""(double quote)  And &nbsp token with space
                if("&quot;" in content):
                    content=content.replace("&quot;","\"")
                elif("&quot" in content):
                    content=content.replace("&quot","\"")
                if("&nbsp;" in content):
                    content=content.replace("&nbsp;"," ")
                elif("&nbsp" in content):
                    content=content.replace("&nbsp"," ")
                content=content.strip()
                #content=content.replace("&quot","\"")
                #content=content.replace("&nbsp"," ")
        else:
            contentnodelist=soup.findAll('td', {'class': 'story'})
            content=""
            for contentnode in contentnodelist:

                #get children of contentnode
                children = contentnode.findChildren()
                
                flag=False;
                for child in children:
                    #if (child.get('class')=='storyBold' or child.get('class')=='caption'):
                        #flag=True
                    if((contentnode.get('class') is not None) and ((contentnode.get('class').strip())=="storyBold") ) or ((contentnode.get('class') is not None) and ((contentnode.get('class').strip())=="caption")):
                        flag=True
                        
                
                    
                #Addition of new code        
                eliminated_script_tag=False
                #get children of contentnode
                        
                for child in children:
                    if(child.name=="script"):
                        eliminated_script_tag=True
                        #Get the eliminated _script_tag string
                        eliminated_string=child.string
                        #End of new code        
                        
                    

                if(flag==False):
                       
                    content=content+" "+' '.join( contentnode.findAll(text=True, recursive=True))
                    #replace &quote token with ""(double quote)  And &nbsp token with space
                    #content=content.replace("&quot","\"")
                    #content=content.replace("&nbsp;"," ")
                    if("&quot;" in content):
                        content=content.replace("&quot;","\"")
                    elif("&quot" in content):
                        content=content.replace("&quot","\"")
                    if("&nbsp;" in content):    
                        content=content.replace("&nbsp;"," ")
                    elif("&nbsp" in content):
                        content=content.replace("&nbsp"," ")
                                    
                    if(eliminated_script_tag==True):
                        content=content.replace(eliminated_string," ")                                    
                else:
                    continue
                
        content=content.strip()
        item['childlinkcontent']['content']=content
        yield item['childlinkcontent']
        #self.extractDataFromJsonFile()

        
    #print item['childlinkcontent']['headline']
    def writeToFile(self,topicdict,topicname,story):
            #topicdict[topicname]
            
            url=story['url']
            headline=story['headline']
            datetime=story['datetime']
            content=story['content']    
            filetobewritten=topicdict[topicname]['filename']
            filereference=topicdict[topicname]['filepointer']
            filereference.write("\n \n ")
            filereference.write(headline.encode("utf-8"))
            filereference.write("\n \n ")
            filereference.write(datetime.encode("utf-8"))
            filereference.write("\n \n \n \n")
            filereference.write(content.encode("utf-8"))
            filereference.write("\n \n ")
            filereference.write(url.encode("utf-8"))
            filereference.write("\n \n ")
            
            
            
    def extractDataFromJsonFile(self):
            basepath="/home/indan/WebCrawler/"
            filename="top-stackoverflow-questions.json"
            file_full_path=basepath+filename
            directory = os.path.dirname(file_full_path)
            #print directory
            if not os.path.exists(directory):
                os.makedirs(directory)
           
            #Get todayDateTime
            import time
            datestring=time.strftime("%d-%m-%Y")
            #print datestring
            resultfoldername="CrawlResult_"+datestring
            resultfolder_full_path_directory=basepath+resultfoldername
            if not os.path.exists(resultfolder_full_path_directory):
                os.makedirs(resultfolder_full_path_directory)
            
            
            with open(file_full_path) as data_file:
                storylist = json.load(data_file)
            topicdict={}
            for story  in   storylist:
                url=story['url']
                #Split the url and get the topic name
                urlsplittedarray=url.split("/")
                urlsplittedarraylength=len(urlsplittedarray)
                topicname=urlsplittedarray[urlsplittedarraylength-2]
                
                if topicname not in topicdict:
                    filename=topicname+".rtf"
                    topicfilenamepath=resultfolder_full_path_directory+"/"+filename
                    
                    directory = os.path.dirname(topicfilenamepath)            
                    if not os.path.exists(directory):
                        os.makedirs(directory)
                        
                    # Open a file
                    fo = open(topicfilenamepath, "w")            
                    topicdict[topicname]={}
                    topicdict[topicname]['filename']=topicfilenamepath
                    topicdict[topicname]['filepointer']=fo
                    self.writeToFile(topicdict,topicname,story)
                else:
                    self.writeToFile(topicdict,topicname,story)
                    
            #print topicdict
            #close the filepointer
            
            for key in topicdict:
                #Get the file pointer
                filepointer=topicdict[key]['filepointer']
                filepointer.close()
