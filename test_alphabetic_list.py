import nltk
from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize
from nltk import FreqDist
from pymongo import MongoClient
import sys
import os
import datetime
import time
import dateutil.parser
import re
import operator

delimeterlist=['.','"','(',')','?','!',',','{','}','[',']','*','-','--','/',';','`','~','@','$','%','^','&','*','+','*','/','\\','|','<','>',':','_','\'',' ']

def getSentenceLength(sentence):
    
    sentencecontent=sentence.split()
    count=0
    print sentencecontent
    
    for word in sentencecontent:
        if word not in delimeterList:
            count=count+1
        else:
            continue


    return count

def dataprocess(contentString):
    """
    The function takes input string as parameter
    and generate tokens and returns the token list
    :param string:
   
    """
    newcontentstring=""
    contentString=contentString.replace('\"','"')
    
    if "\n" in contentString:
        contentStringList=contentString.split("\n")
        endmarkerlist=['.','!','?']
        for contentString in contentStringList:
            #Get the last character of the string.
            endmarker=contentString[:-1]
            #Add end marker if the string does not contain '.'
            if endmarker not in endmarkerlist:
                contentString=contentString+"."
            newcontentstring=newcontentstring+contentString    
            
    else:
        newcontentstring=contentString
        
    #'&'
    

    for delimeter in delimeterlist:
        newdelimeter=" "+delimeter+" "
        newcontentstring=newcontentstring.replace(delimeter,newdelimeter)
    return newcontentstring

def removeInvalidToken(tokenlist):
    
    validTokenList=[]
    for item in tokenlist:
        if (item in delimeterlist) or (item.isdigit()==True):
            continue
        if(len(item)==1) and (item!="A" and item!="a"):
            continue
        validTokenList.append(item)
       
    return  validTokenList    
            


if __name__ == '__main__':



    contentString="Thank You everyone for your heartfelt wishes! The day was made even grand by appreciation and love that met me! Excitement is still high! Celebrations will persist!!! #Google #JobPlacements #WantNYCAgain\", he wrote with an apt emotion - awesome. With his job offer, Ashutosh has become the first student from IIT-Patna to get a job at Google. He said: \"My placement with Google will open doors of IIT for Google and other top IT companies in the world."
    contentString=dataprocess(contentString)
    print contentString
    tokens = nltk.word_tokenize(contentString)
    print tokens
    print "Hello"
        
    #print distinct_tokens ignoring case
    distinct_tokens= list(set(x  for x in tokens))
    
    distinct_tokens=removeInvalidToken(distinct_tokens)    
    
    #count the total
    distinct_tokens_count=len(distinct_tokens)
      
    tokenlist=[]

    for distinct_token in distinct_tokens:
        token=distinct_token
        tokenlen=len(token)

        tokensublist=[]
        tokensublist.append(token)
        tokensublist.append(tokenlen)
        tokensubtuple=tuple(tokensublist)
        tokenlist.append(tokensubtuple)

    #print tokendict
    import operator
    tokenlist_sorted = sorted(tokenlist, key=operator.itemgetter(1),reverse=True)

    #print tokenlist_sorted
    globaltokenlist=[]
    for key in tokenlist_sorted:
        tokensubtuple=key

        #Fetch Token and Token Length
        token=str(tokensubtuple[0])
        #globaltokenlist.append(token)
        tokenlen=str(tokensubtuple[1])

        #write it to file
        print(token+"::"+tokenlen)
        print("\n")


    #Generate Token list for frequency distribution calculation
    globaltokenlist=removeInvalidToken(tokens)
    #globaltokenlist=removeInvalidToken(globaltokenlist)
    
    #return globaltokenlist
    
    #tokenlist=[("Arpita",6),("arpita",844),("Dona",5),("dona",8)]
    #tokenlist_sorted = sorted(tokenlist, key=lambda x:(x[0].lower,x[1]),reverse=False)
    #print tokenlist_sorted
    #sentence="They tried to increase the base so that more athletes are part of the Olympic sport,\"; he added.Hello.It's Thursday, December 3, 2015."
    #delimeterList=['?','.','!']
    ##Sentence Tokennize Operation
    
    #sentence=sentence.replace("."," . ")        
    #sentenceList = sent_tokenize(sentence.strip())
    #for sentence in sentenceList:
        #print sentence
        
        #count=getSentenceLength(sentence)
        #print count
    
    
    
    