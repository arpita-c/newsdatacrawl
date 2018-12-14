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


path="/home/arpita/Documents/NLP_ANALYSIS/Report/"

def writeContentToFile(cursor):
    """
    This function writes content which has been fetched from database to the file
    and add the content in a string variable
    """
    #create  the filename
    filename=path+"content.rtf"

    #create a file pointer
    fp=open(filename,"wb+")

    #create a string variable
    contentString=""

    #write it to file
    for document in cursor:
        id=str(document['_id'])
        #fp.write(id)
        content=document['Content']
        content=content.replace("\\\";","\"")
        content=content.replace("\\","" )
        
        fp.write(content)
        
        contentString=contentString+" "+content+" "
        fp.write("\n")

    #close the file pointer
    fp.close()
    #print contentString
    return contentString


def tokenizeWord(contentString):
    """
    The function takes input string as parameter
    and generate tokens and returns the token list
    :param string:

    """

    #tokenize operation
    tokens = nltk.word_tokenize(contentString)

    #print distinct_tokens
    distinct_tokens= list(set(tokens))

    #create  the filename for listing token
    filename=path+"token.rtf"

    #create a file pointer
    fp=open(filename,"wb+")


    #count the total
    distinct_tokens_count=len(distinct_tokens)

    fp.write("Total Token Count="+str(distinct_tokens_count))
    fp.write("\n")
    fp.write("Token List::Length")
    fp.write("\n")
    fp.write("\n")

    fp.write("########################################################")
    fp.write("\n")
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

    for key in tokenlist_sorted:
        tokensubtuple=key

        #Fetch Token and Token Length
        token=str(tokensubtuple[0])
        tokenlen=str(tokensubtuple[1])

        #write it to file
        fp.write(token+"::"+tokenlen)
        fp.write("\n")


    fp.write("\n")
    fp.write("########################################################")

    #close the file pointer
    fp.close()


def getSentenceLength(sentence):
    sentencecontent=sentence.split()
     #re.split(r'(;|,|\s)\s*', line)
    sentenceAfterSplit1 = re.split(r'[\s,;\.\'\"\)\(]+', sentence)
    sentenceAfterSplit2 = re.split(r'[\s,;-_!#?/\\\-\.\'\"\)\(\:]+', sentence)
    #print sentenceAfterSplit
    return sentenceAfterSplit1,sentenceAfterSplit2,len(sentencecontent)




def sentenceDetect(contentString):
    """
    The function takes input string as parameter
    and generate sentence and returns the sentence list
    :param string:
    :return:sum of all token list taken for each sentence
    """
    #Sentence Tokennize Operation
    sent_tokenize_list = sent_tokenize(contentString)

    #Count the total number of sentence
    sentenceCount=len(sent_tokenize_list)

    #create  the filename for listing token
    filename=path+"sentence.rtf"

    #create a file pointer
    fp=open(filename,"wb+")

    fp.write("Total Sentence Count="+str(sentenceCount))
    fp.write("\n")
    fp.write("sentence List::Length")
    fp.write("\n")
    fp.write("\n")

    fp.write("########################################################")
    fp.write("\n")

    wordtokenGlobalList=[]
    wordtokenGlobalListRefined=[]
    for sentence in sent_tokenize_list:


        #get the sentence Length without punctuation
        wordtoken,worktokenrefined,sentencelength=getSentenceLength(sentence)
        fp.write(sentence+"::"+str(sentencelength))

        #add sentence token to global token list
        wordtokenGlobalList.extend(wordtoken)
        wordtokenGlobalListRefined.extend(worktokenrefined)
        fp.write("\n")
        #fp.write(str(wordtokenGlobalList))
        fp.write("\n \n \n")



    #close the file pointer
    fp.close()
    return wordtokenGlobalList,wordtokenGlobalListRefined





def finetokenizeWord1(wordtokenGlobalList):


    distinct_tokens= list(set(wordtokenGlobalList))
    #print distinct_tokens
    #create  the filename for listing token
    filename=path+"tokenRefined1.rtf"

    #create a file pointer
    fp=open(filename,"wb+")


    #count the total
    distinct_tokens_count=len(distinct_tokens)
    #fp.write(str(distinct_tokens))

    fp.write("Total Token Count="+str(distinct_tokens_count))
    fp.write("\n")
    fp.write("Token List::Length")
    fp.write("\n")
    fp.write("\n")

    fp.write("########################################################")
    fp.write("\n")
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

    for key in tokenlist_sorted:
        tokensubtuple=key

            #Fetch Token and Token Length
        token=str(tokensubtuple[0])
        tokenlen=str(tokensubtuple[1])

        #write it to file
        fp.write(token+"::"+tokenlen)
        fp.write("\n")


    fp.write("\n")
    fp.write("########################################################")

    #close the file pointer
    fp.close()




def finetokenizeWord2(wordtokenGlobalList):


    distinct_tokens= list(set(wordtokenGlobalList))
    #print distinct_tokens
    #create  the filename for listing token
    filename=path+"tokenRefined2.rtf"

    #create a file pointer
    fp=open(filename,"wb+")


    #count the total
    distinct_tokens_count=len(distinct_tokens)
    #fp.write(str(distinct_tokens))

    fp.write("Total Token Count="+str(distinct_tokens_count))
    fp.write("\n")
    fp.write("Token List::Length")
    fp.write("\n")
    fp.write("\n")

    fp.write("########################################################")
    fp.write("\n")
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

    for key in tokenlist_sorted:
        tokensubtuple=key

            #Fetch Token and Token Length
        token=str(tokensubtuple[0])
        tokenlen=str(tokensubtuple[1])

        #write it to file
        fp.write(token+"::"+tokenlen)
        fp.write("\n")


    fp.write("\n")
    fp.write("########################################################")

    #close the file pointer
    fp.close()




def getFrequencyDistribution(wordtokenGlobalList):
    """
    This function collects the global token list and writes the frequency distribution list
    into a file
    :param wordtokenGlobalList:
    :return:
    """
    fdist = FreqDist(wordtokenGlobalList)

    filename=path+"FreqDistRefined0.rtf"

    #create a file pointer
    fp=open(filename,"wb+")

    keylist=fdist.keys()
    #fp.write(str(keylist))
    fp.write("\n")
    tokenlist=[]

    for key in keylist:
        if key=='':
            continue
        token=str(key)
        frequency=fdist[key]

        tokensublist=[]
        tokensublist.append(token)
        tokensublist.append(frequency)
        tokensubtuple=tuple(tokensublist)
        tokenlist.append(tokensubtuple)


    import operator
    tokenlist_sorted = sorted(tokenlist, key=operator.itemgetter(1),reverse=True)

    #print tokenlist_sorted

    for key in tokenlist_sorted:

        tokensubtuple=key

        #Fetch Token and Token Length
        token=str(tokensubtuple[0])
        tokenlen=str(tokensubtuple[1])

        fp.write(token+"=>"+tokenlen)
        fp.write("\n")
        #print (key+"=>"+ str(fdist[key]))
    #fp.write(str(fdist.keys()))

    fp.close()



def getFrequencyDistributionRefined(wordtokenGlobalList):
    """
    This function collects the global token list and writes the frequency distribution list
    into a file
    :param wordtokenGlobalList:
    :return:
    """
    fdist = FreqDist(wordtokenGlobalList)

    filename=path+"FreqDistRefined1.rtf"

    #create a file pointer
    fp=open(filename,"wb+")

    keylist=fdist.keys()
    #fp.write(str(keylist))
    fp.write("\n")
    tokenlist=[]

    for key in keylist:
        if key=='':
            continue
        token=str(key)
        frequency=fdist[key]

        tokensublist=[]
        tokensublist.append(token)
        tokensublist.append(frequency)
        tokensubtuple=tuple(tokensublist)
        tokenlist.append(tokensubtuple)


    import operator
    tokenlist_sorted = sorted(tokenlist, key=operator.itemgetter(1),reverse=True)

    #print tokenlist_sorted

    for key in tokenlist_sorted:

        tokensubtuple=key

        #Fetch Token and Token Length
        token=str(tokensubtuple[0])
        tokenlen=str(tokensubtuple[1])

        fp.write(token+"=>"+tokenlen)
        fp.write("\n")
        #print (key+"=>"+ str(fdist[key]))
    #fp.write(str(fdist.keys()))

    fp.close()




if __name__ == '__main__':


    #input date
    startdate=datetime.datetime(2015, 12, 01)

    #end Date
    enddate=datetime.datetime(2015, 12, 31)
    #create connection to MongoDb
    client = MongoClient()

    #Now Connect create to TelegraphData Database
    db=client.TelegraphData

    #Fetch content from database based on the date
    cursor=db.master.find({"Date": {"$gte":startdate,"$lte":enddate}})

    #Get the content of the corpora
    contentString=writeContentToFile(cursor)

    #make tokenization of the ContentString
    tokenizeWord(contentString)

    #create globaltokenlist unique word list
    #wordtokenGlobalList,wordtokenGlobalListRefined=sentenceDetect(contentString)

    #wordtokenGlobalList is the global token list where each token set is taken from each sentence and then append
    #to wordtokenGlobalList

    #Now we are gonna do 2nd level of token filtering.
    #finetokenizeWord1(wordtokenGlobalList)


    #Frequency distribution of the wordlist
    #getFrequencyDistribution(wordtokenGlobalList)



    #Now we are gonna do 3rd level of token filtering
    #finetokenizeWord2(wordtokenGlobalListRefined)

    #Frequency Distribution of the refined wordlist
    #getFrequencyDistributionRefined(wordtokenGlobalListRefined)


    #print contentString