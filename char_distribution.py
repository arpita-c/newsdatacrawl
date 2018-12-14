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
delimeterlist=['.','"','(',')','?','!',',','{','}','[',']','*','-','/',';','`','~','@','$','%','^','&','*','+','*','/','\\','|','<','>',':',' ','_','\'']
#'\''
def separateStringWithEndTag(item):
    
    #Get the last character of the string
    lastcharacter=item[-1:]
    endmarkerlist=['.','?','!']
    if lastcharacter not in endmarkerlist:
        #There is a susbsection heading ,which we dont want in sentence or token as it implies heading informatopn
        #We need to be sure whether entire item is valid/invalid sentence
        
        #Now we try to find valid sentence from the item string(if exists)
        
        # Now we search for whether there is any end marker exists in the content  before  the last character.
        prev_marker=0;
        current_marker=0;
        
        for endmarker in endmarkerlist:
        
            current_marker=item.rfind(endmarker)
            if(prev_marker<current_marker):
                prev_marker=current_marker          
                
       
        #prev_marker stores highest value of the last index of endmarker
        if prev_marker>0:
            #Fetch the valid string
            endmarked_string=item[:prev_marker+1]
            
            
            #GET THE End_Mark Tag less string/invaild sentence
            firstindex=prev_marker+2
            lastindex=len(item)
            end_mark_less_string=item[firstindex:lastindex]
            return endmarked_string,end_mark_less_string
        
        else:
            return "",item
            

    else:
        return item,""
    
def writeContentToFile(cursor):
    """
    This function writes content which has been fetched from database to the file
    and add the content in a string variable
    """
    #create  the filename
    path="/home/arpita/Documents/NLP_ANALYSIS/Report/"
    filename=path + "content.rtf"
    posContentFilename=path+"posContent.rtf"
    posSentenceFilename=path+"posSentence.rtf"
    posSegmentFilename=path+"posSegment.rtf"
    #create a file pointer
    fp=open(filename,"wb+")
    fposcontent=open(posContentFilename,"wb+")
    fpossentence=open(posSentenceFilename,"wb+")
    fposegment=open(posSegmentFilename,"wb+")
    #create a string variable
    #contentstring::Valid String
    contentString=""
    endmarkerlist=['.','?','!']
    #write it to file
    import unicodedata
    for document in cursor:
        id=str(document['_id'])
        #fp.write(id)
        content=document['Content']
        documentValidString=""
        
        content=content.replace("\\\";","\"")
        content=content.replace("&amp;","&")
        #search for \n in the content
        subsectionheading=""
        if "\n" in content :
            fp.write("\n <STARTTAG> \n")
            fposcontent.write("\n <STARTTAG> \n")
            contentlist=content.split("\n")
            for item in contentlist:
                #Get the last character of the content
                item=item.rstrip()
                if(len(item)==0 ):
                    continue
                index=len(item)-1
                itemstring=item.encode('ascii','ignore')
                #Remove trailing spaces to identify the last character
                
                validstring,invalidstring=separateStringWithEndTag(item)
                if(len(validstring)>0):
                    fp.write("\n"+validstring+"\n")
                    fposcontent.write("\n"+validstring+"\n")
                    contentString=contentString+" "+validstring+" "
                    documentValidString=documentValidString+" "+validstring+" "
                    
                if(len(invalidstring)>0):    
                    subsectionheading="\n <SUBSECTION_HEADING_STARTTAG> \n"+invalidstring+"\n <SUBSECTION_HEADING_ENDTAG> \n"
                    fp.write(subsectionheading)
                    
     
            fp.write("\n <ENDTAG> \n")
            fposcontent.write("\n <ENDTAG> \n")
                    
        else:
            fp.write("\n <STARTTAG> \n")
            fposcontent.write("\n <STARTTAG> \n")
            validstring,invalidstring=separateStringWithEndTag(content)
            if(len(validstring)>0):
                fp.write("\n"+validstring+"\n")
                fposcontent.write("\n"+validstring+"\n")
                contentString=contentString+" "+validstring+" "
                documentValidString=documentValidString+" "+validstring+" "
                
                
            if(len(invalidstring)>0):    
                subsectionheading="\n <SUBSECTION_HEADING_STARTTAG> \n"+invalidstring+"\n <SUBSECTION_HEADING_ENDTAG> \n"
                fp.write(subsectionheading)
                            
                     
            fp.write("\n <ENDTAG> \n")
            fposcontent.write("\n <ENDTAG> \n")
            
            fpossentence.write("\n <STARTTAG> \n")
            fposegment.write("\n <STARTTAG> \n")        
            sentenceDetection(documentValidString, fposegment, fpossentence)
            fpossentence.write("\n <ENDTAG> \n")
            fposegment.write("\n <ENDTAG> \n")
            
            fpossentence.write("\n")
            fposegment.write("\n")            
            
    
    fp.write("\n")
    fposcontent.write("\n")
    #close the file pointer
    fp.close()
    fposcontent.close()
    fpossentence.close()
    fposegment.close()
    #print contentString
    return contentString


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
    



def tokenizeWord(contentString):
    """
    The function takes input string as parameter
    and generate tokens and returns the token list
    :param string:

    """

    #tokenize operation
    #print contentString
    tokens = nltk.word_tokenize(contentString)
        
    #print distinct_tokens ignoring case
    distinct_tokens= list(set(x  for x in tokens))
    
    distinct_tokens=removeInvalidToken(distinct_tokens)    
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
    globaltokenlist=[]
    for key in tokenlist_sorted:
        tokensubtuple=key

        #Fetch Token and Token Length
        token=str(tokensubtuple[0])
        #globaltokenlist.append(token)
        tokenlen=str(tokensubtuple[1])

        #write it to file
        fp.write(token+"::"+tokenlen)
        fp.write("\n")


    fp.write("\n")
    fp.write("########################################################")

    #close the file pointer
    fp.close()
    #Generate Token list for frequency distribution calculation
    globaltokenlist=removeInvalidToken(tokens)
    #globaltokenlist=removeInvalidToken(globaltokenlist)
    
    return globaltokenlist


#def getSentenceLength(sentence):
    #sentencecontent=sentence.split()
     ##re.split(r'(;|,|\s)\s*', line)
    ##sentenceAfterSplit1 = re.split(r'[\s,;\.\'\"\)\(]+', sentence)
    ##sentenceAfterSplit2 = re.split(r'[\s,;-_!#?/\\\-\.\'\"\)\(\:]+', sentence)
    ##print sentenceAfterSplit
    ##return sentenceAfterSplit1,sentenceAfterSplit2,len(sentencecontent)
    #return len(sentencecontent)




#def sentenceDetect(contentString):
    #"""
    #The function takes input string as parameter
    #and generate sentence and returns the sentence list
    #:param string:
    #:return:sum of all token list taken for each sentence
    #"""
    ##Sentence Tokennize Operation
    #sent_tokenize_list = sent_tokenize(contentString)

    ##Count the total number of sentence
    #sentenceCount=len(sent_tokenize_list)

    ##create  the filename for listing token
    #filename=path+"sentence.rtf"

    ##create a file pointer
    #fp=open(filename,"wb+")

    #fp.write("Total Sentence Count="+str(sentenceCount))
    #fp.write("\n")
    #fp.write("sentence List::Length")
    #fp.write("\n")
    #fp.write("\n")

    #fp.write("########################################################")
    #fp.write("\n")

    #wordtokenGlobalList=[]
    #wordtokenGlobalListRefined=[]
    #for sentence in sent_tokenize_list:


        ##get the sentence Length without punctuation
        ##wordtoken,worktokenrefined,sentencelength=getSentenceLength(sentence)
        #sentencelength=getSentenceLength(sentence)
        #fp.write(sentence+"::"+str(sentencelength))

        ##add sentence token to global token list
        ##wordtokenGlobalList.extend(wordtoken)
        ##wordtokenGlobalListRefined.extend(worktokenrefined)
        #fp.write("\n")
        ##fp.write(str(wordtokenGlobalList))
        #fp.write("\n \n \n")



    ##close the file pointer
    #fp.close()
    ##return wordtokenGlobalList,wordtokenGlobalListRefined





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
    #distinct_token=removeInvalidToken(distinct_tokens)
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



def removeInvalidToken(tokenlist):
    
    validTokenList=[]
    for item in tokenlist:
        if (item in delimeterlist) or (item.isdigit()==True):
            continue
        if(len(item)==1) and (item!="A" and item!="a"):
            continue
        validTokenList.append(item)
       
    return  validTokenList    
            
            
    
    
def getFrequencyDistributionSorted(wordtokenGlobalList):
    """
    This function collects the global token list and writes the frequency distribution list
    into a file
    :param wordtokenGlobalList:
    :return:
    """
    fdist = FreqDist(wordtokenGlobalList)

    filename=path+"FreqDistSorted.rtf"

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
    #tokenlist_sorted = sorted(tokenlist, key=lambda s: s.lower(),reverse=True)
    
    #print tokenlist_sorted

    for key in tokenlist_sorted:

        tokensubtuple=key

        #Fetch Token and Token Length
        token=str(tokensubtuple[0])
        tokenlen=str(tokensubtuple[1])

        #fp.write(token+"=>"+tokenlen)
        fp.write(token+" \t "+tokenlen)
        
        fp.write("\n")
        #print (key+"=>"+ str(fdist[key]))
    #fp.write(str(fdist.keys()))

    fp.close()



def getFrequencyDistribution(wordtokenGlobalList,month):
    """
    This function collects the global token list and writes the frequency distribution list
    into a file
    :param wordtokenGlobalList:
    :return:
    """
    fdist = FreqDist(wordtokenGlobalList)

    filename=path+"FreqDistRefined.rtf"

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
    #tokenlist_sorted = sorted(tokenlist, key=operator.itemgetter(1),reverse=True)
    #tokenlist_sorted = sorted(tokenlist, key=lambda x:(x[0].lower),reverse=False)
    tokenlist_sorted=tokenlist
    case_sensitive_equal_token_list=[]
    unique_token_list=[]
    marked_token_list={}
    for index,val in enumerate(tokenlist_sorted):
        token=str(val[0])
        markedToken=token.lower()
        
        if marked_token_list.has_key(markedToken)==False:
            marked_token_list[markedToken]=[]
            marked_token_list[markedToken].append(val)
            
        else:
            marked_token_list[markedToken].append(val)
            #marked_token_list[markedToken]
            #case_sensitive_equal_token_list_temp=[]
            #case_sensitive_equal_token_list_temp.append(index)
            ##check for matching string for the token with different case
            #for index1,val1 in enumerate(tokenlist_sorted):
                #matchedToken=str(val1[0])
                #if( (matchedToken!=token) and (matchedToken.lower==token.lower) ):
                    #case_sensitive_equal_token_list_temp.append(index1)
                    
            #case_sensitive_equal_token_list.append(case_sensitive_equal_token_list_temp)
            #marked_token_list[markedToken]=1
        
        if markedToken not in unique_token_list:
            unique_token_list.append(markedToken)
            
    #print marked_token_list
    unique_token_list=sorted(unique_token_list, reverse=False)
    #create a mysql connection
    
    import MySQLdb
    
    # Open database connection
    db = MySQLdb.connect("localhost","root","root","NewsDataAnalysis")
    
    # prepare a cursor object using cursor() method
    cursor = db.cursor()    

    for key in unique_token_list:

        tokensubtuple=key
        valList=marked_token_list[key]
        
        for tokensubtuple in valList:
            #Fetch Token and Token Length
            token=str(tokensubtuple[0])
            tokenlen=str(tokensubtuple[1])
    
            #fp.write(token+"=>"+tokenlen)
            fp.write(token+" \t "+tokenlen)
            
            writeFrequencyCountDb(cursor,month,token,tokenlen)
            fp.write("\n")
            #print (key+"=>"+ str(fdist[key]))
        #fp.write(str(fdist.keys()))

    fp.close()
    # Commit your changes in the database
    db.commit()
    
    # disconnect from server
    db.close()    


    
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





def getIndexOfDotCharacter(sentence):

    delimeterList=['"','(',')','?','!',',','{','}','[',']','*','-','/',';','`','~','@','$','%','^','&','*','+','*','/','\\','|','<','>',':','_','\'',' ']
    sentence=sentence.replace("."," . ")
    sentenceContentList=sentence.split()
    dotIndexList=[]

    for index,word in enumerate(sentenceContentList):

        if word not in delimeterList:
            #print word
            if (word == "."):
                dotIndexList.append(index)

    #Get the last index of dot character in the list
    #Get the length of dotIndexList length
    lendotIndexList=len(dotIndexList)
    lastDotCharcaterIndex=dotIndexList[lendotIndexList-1]
    secondlastDotCharcaterIndex=dotIndexList[lendotIndexList-2]

    #Check the difference::
    diff=lastDotCharcaterIndex-secondlastDotCharcaterIndex
    if(diff<=2):
    #It should merge with the next string
        return True
    else:
        return False

def getSentenceLength(sentence):
    delimeterList=['.','"','(',')','?','!',',','{','}','[',']','*','-','/',';','`','~','@','$','%','^','&','*','+','*','/','\\','|','<','>',':','_','\'',' ']

    sentencecontent=sentence.split()
    count=0
    for word in sentencecontent:
        if word not in delimeterList:
            count=count+1
        else:
            continue


    return count



def lastCharIsNumber(sentence):

    #Get the index of "."
    sentence=sentence.strip()
    lastcharIndex=sentence.find(".")

    #Get the last character
    lastChar=sentence[lastcharIndex-1]

    if str(lastChar).isdigit()==True:
        return True
    else:
        return False


def firstCharIsNumber(sentence):

    sentence=sentence.strip()
    #Get the first character
    firstchar=sentence[:1]
    if((str(firstchar).isdigit())==True):
        return True
    else:
        return False    


def removeSemiColon1stPlace(sentence):
    #Get the first Character
    firstChar=sentence[:1]
    if(str(firstChar)==";"):
        sentence=sentence[1:]
        return sentence
    else:
        return sentence



def checkForSegmentString(fileStr,segmentfilePointer):
    fileStr=fileStr.strip()
    index=fileStr.find(':')
    #print index
    #get the string from first index to segment index
    if(index>=0):
        segmentstring=fileStr[0:index]
        tempSegmentString=segmentstring
        #Get the len of the segment string (Not considering )
        segmentStrLen=getSentenceLength(tempSegmentString);
        if(segmentStrLen<=5):
            #We are sure it is metadata,we will preserve the string in another file
            segmentfilePointer.write(segmentstring)
            segmentfilePointer.write("\n")
            segmentfilePointer.write("=>"+fileStr)
            segmentfilePointer.write("\n \n")
            #segmentfilePointer.close()
            fileStr=fileStr[index+1:]
            fileStr=fileStr.strip()
            return fileStr
        else:
            return fileStr
    else:
        return fileStr






def sentenceDetection(contentString,segmentfilePointer,sentencefilePointer):
 
    fileStr=contentString
    
    delimeterList=['.','"','(',')','?','!',',','{','}','[',']','*','-','/',';','`','~','@','$','%','^','&','*','+','*','/','\\','|','<','>',':','_','\'',' ']
        
    fileStr=fileStr.replace("...",".")
    fileStr=fileStr.replace(".",". ")    
    delimeterList=['?','.','!']
    #Sentence Tokennize Operation
    sentenceList = sent_tokenize(fileStr.strip())
    indextobeIgnored=[]
    for index,sentence in enumerate(sentenceList):
        #print index
        if(index in indextobeIgnored):
            #print indextobeIgnored
            continue
        sentence=checkForSegmentString(sentence,segmentfilePointer)
        #Get the no of words in sentence
        tempSentenceString=sentence
        
        #Get the no of count '.' present in string
        countDotCharacter=tempSentenceString.count(".")
        
        if countDotCharacter==1:
            #Still We need to check whether it contains any internet link or number
            #get the length of next sentence
            count=1
            indexNo=index+count
            if(indexNo<=len(sentenceList)-1):
                
                #Get the last character of the sentence to check it is number
                lastCharisNumberStatus=lastCharIsNumber(sentence)
                #Get the first character of the next sentence to check it is number
                firstCharIsNumberStatus=firstCharIsNumber(sentenceList[indexNo])
                
                if((lastCharisNumberStatus is True) and (firstCharIsNumberStatus is True)):
                    
                    sentence=sentence+sentenceList[indexNo]
                    indextobeIgnored.append(indexNo)
                
                else:
                    while(True):
                        
                        indexNo=index+count
                        if(indexNo<=len(sentenceList)-1):
                            nextsentence=sentenceList[indexNo]
                            lennextSentence=getSentenceLength(sentenceList[indexNo])
                            
                            if((lennextSentence==1 ) and (nextsentence.find(".")>=0)):
                                sentence=sentence+nextsentence
                                indextobeIgnored.append(indexNo)
                                count=count+1
                            else:
                                break
                            
                            
                        else:
                            break
        
        if countDotCharacter>1:
            #Merge the sentence with the next sentence
            #Because there might be possiblity dot character signifies different meaning 
            #like name abbreviation,or some internet site name.We dont wanna loose sentence consistency
            
            count=1
            while(True):
                tobemergeStatus=getIndexOfDotCharacter(sentence)
                if(tobemergeStatus==True and (index+count)<len(sentenceList)):
                    nextsentence=str(sentenceList[index+count])
                
                    countDotCharacterNext=nextsentence.count(".")
                    sentence=sentence+nextsentence
                    nextindex=index+count
                    indextobeIgnored.append(nextindex)
                    #print nextsentence+"::"+str(nextindex)+"::"+str(countDotCharacterNext)
                    #print("\n")
                    if((countDotCharacterNext>1) and (getIndexOfDotCharacter(nextsentence)==True)):
                        count=count+1
                    else:
                        break
                else:
                    break
            #indextobeIgnoredEnd=index+count
        
        #Get rid of 1st character of the sentence if it is semicolon.
        sentence=removeSemiColon1stPlace(sentence)
            
        #Get the len of the segment string (Not considering )
        sentenceStrLen=getSentenceLength(sentence)    
        #Print the  wordlength of the sentence
        wordlengthStr="Word Strength  "+str(sentenceStrLen)
        sentence=sentence.replace(". ",".")
        sentencefilePointer.write(sentence)
        sentencefilePointer.write("\n")
        #sentencefilePointer.write("\n")
        sentencefilePointer.write(wordlengthStr)
        sentencefilePointer.write("\n")
        sentencefilePointer.write("\n")
        sentencefilePointer.write("\n")
    #sentencefilePointer.close()
    #segmentfilePointer.close()
    
    
    
def insertTokenDetails(globaltokenlist,databasemonth,client):
    
    #Now Connect to TelegraphData Database
    db=client.TelegraphData["TokenDetails"]
    
    for token in globaltokenlist:
        postdata={"databasename":databasemonth,"token":token}
        result=db.insert(postdata)
        
    

def chardistribution(month,contentString):
    
    from collections import Counter
    counterPointer = Counter()
    counterPointer += Counter(contentString)
    charDict = dict(counterPointer)
    import MySQLdb

    # Open database connection
    db = MySQLdb.connect("localhost","root","root","NewsDataAnalysis")

    # prepare a cursor object using cursor() method
    cursor = db.cursor()    
    
    try:
        print "started Insertion"
        for item in charDict:
            character=str(item)
            countval=str(charDict[character])        
            if(character.isalnum()==True or character=="$" or character=="." or character=="@"):
                querySql="INSERT INTO `NewsDataAnalysis`.`CharDistribution` (`month`, `character`, `count`) VALUES ('"+ \
                    month+"','"+ character+"','"+countval+"');"        
                 
                execute(cursor, querySql)
                db.commit()
            else:
                continue
    except:
        db.rollback()
        
    finally:
        cursor.close()
        db.close()
 
    
def execute(cursor,sql):
    """Run the SQL statement against the object's database connection"""
    import MySQLdb

    # Try to run the sql
    try:

        cursor.execute(sql)

        return True

    except MySQLdb.Warning, e:

        # Log the warning as an error in the error log
        print(e.message)

        # Log this warning in the Watson database
        print("Database Warning", e.message, sql[:256])

    except Exception as e:

        # Did we lose connection with the server?
        if e.args == (2006, 'MySQL server has gone away'):

            # Log a message
            print("execute: ERROR: " + \
                                   "Lost connection with server...attempting" + \
                                   "to reconnect")
        # Did we try to insert a duplicate entry in a unique index?
        elif e.args[0] == 1062:

                # Log an error in the log file
            print("execute: ERROR: " + \
                 "Could not rollback transaction: " + sql)

            return "Duplicate"

        # Different MySQL error...
        else:
            # Log an error in the log file
            print("execute: ERROR: " + \
                                   "Could not commit: " + sql)

            
        return False




def writeCharacterFrequencyDb(month,charDict):
    
     
    #Loop through each character Dictionary
    for item in charDict:
        character=str(item)
        
        querySql="INSERT INTO `NewsDataAnalysis`.`CharDistribution` (`month`, `character`, `count`) VALUES ('"+ \
                 month+"','"+ character+"','"+countval+"');"
        print querySql
        #Execute Query
        cursor.execute(querySql)
    
    #close the cursor
    cursor.close()
    
    
if __name__ == '__main__':


    #input date
    startdate=datetime.datetime(2015, 8,1)
    #end Date
    enddate=datetime.datetime(2015, 8, 31)

    #create connection to MongoDb
    client = MongoClient()

    #Now Connect create to TelegraphData Database
    db=client.TelegraphData_August_Test
    month='August'
    #Fetch content from database based on the date
    cursor=db.master.find({"Date": {"$gte":startdate,"$lte":enddate}})
    print "Data has been fetched from database"
    
    #Get the content of the corpora
    prevcontentString=writeContentToFile(cursor)
    print "File Conetent has been written to file"
    
    # make data processing on content string
    contentString=dataprocess(prevcontentString)
    
    #GetCharacter Distribution
    chardistribution(month,contentString)    
    
    
    #make tokenization of the ContentString
    #globaltokenlist=tokenizeWord(contentString)
    
    #databasemonth="TelegraphData_December_Test"
    
    #Insert token into database
    #insertTokenDetails(globaltokenlist,databasemonth,client)
    
    #print "Token Generation Complete"

    #create  the filename for listing token
    #filenameSentence=path+"sentenceList.rtf"
    #filenameSegment=path+"segmentList.rtf"
    ##create a file pointer
    #segmentfilePointer=open(filenameSegment,"wb+")
    #sentencefilePointer=open(filenameSentence,"wb+")   
    
    ##create globaltokenlist unique word list
    #sentenceDetection(prevcontentString,segmentfilePointer,sentencefilePointer)
    #sentencefilePointer.close()
    #segmentfilePointer.close()    
    #print "Sentence Detection complete"
    ##wordtokenGlobalList,wordtokenGlobalListRefined=sentenceDetect(contentString)

    #wordtokenGlobalList is the global token list where each token set is taken from each sentence and then append
    #to wordtokenGlobalList

    #Now we are gonna do 2nd level of token filtering.
    #finetokenizeWord1(wordtokenGlobalList)

    #Get valid token list from to make it compaitable for frequencyGeneration
    #globaltokenlist=removeInvalidToken(globaltokenlist)
    
    #Frequency distribution of the wordlist
    #month="December"
    #getFrequencyDistribution(globaltokenlist,month)
    #print "Frequency distribution complete"
    #Get Frequency Distribution of the token list in sorted form with upper case and lower case together
    
    
    #Frequency distribution of the wordlist
    #getFrequencyDistributionSorted(globaltokenlist)
   
    
    
    
    
    #client.close()
    #print ("All Done")

    #Now we are gonna do 3rd level of token filtering
    #finetokenizeWord2(wordtokenGlobalListRefined)

    #Frequency Distribution of the refined wordlist
    #getFrequencyDistributionRefined(wordtokenGlobalListRefined)


    #print contentString