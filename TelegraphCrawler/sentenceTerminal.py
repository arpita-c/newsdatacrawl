import nltk
from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize
from nltk import FreqDist
from pymongo import MongoClient
import sys
import os
import datetime
import time
import os
import sys
import getopt
import traceback
import datetime as dt
import dateutil.parser
import re
from os import path

def getIndexOfDotCharacter(sentence):
   
    delimeterList=['"','(',')','?','!',',','{','}','[',']','*','-','/',';','`','~','@','$','%','^','&','*','+','*','/','\\','|','<','>',':','_','\'',' ']
    sentence=sentence.replace("."," . ")
    sentenceContentList=sentence.split()
    dotIndexList=[]
    
    for index,word in enumerate(sentenceContentList):
        
        if word not in delimeterList:
            if word is ".":
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
            segmentfilePointer.write("\n \n")
            #segmentfilePointer.close()
            fileStr=fileStr[index+1:]
            fileStr=fileStr.strip()
            return fileStr
        else:
            return fileStr
    else:
        return fileStr

    
    
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
if __name__ == "__main__":

    # Parse Command Line Arguments
    try:
        # Use getopt module to read flags and values into two lists
        opts, args = getopt.getopt(sys.argv[1:], "f:",
                                   ["ipfile=",
                                    "help" ])

    except getopt.GetoptError:
        print "Couldn't parse arguments correctly"
        sys.exit(2)

    # Initialize variables
    INPUT_FILENAME = None
    
    # Store arguments as variables to run parsing program
    for opt, arg in opts:
        if opt in ("-f", "--ipfile"):
            INPUT_FILENAME = arg
        elif opt == "--help":
            print __doc__
            sys.exit(0)

    # Perform some error checking on the command line arguments. The script cannot
    #  run without some key pieces of information
    if INPUT_FILENAME == None:
        print __doc__
        sys.exit(0)

  
    #Get the base path filename
    basename,filename=os.path.split(INPUT_FILENAME)
    file = open(INPUT_FILENAME, 'r')
    
    #Create segment file 
    #create  the filename for listing token
    if path.exists(basename):
        
        sentencefilepath=os.path.join(basename,'sentenceList.rtf')
        segmentfilepath=os.path.join(basename,'segmentList.rtf')
        #create a file pointer
        segmentfilePointer=open(segmentfilepath,"wb+")
        sentencefilePointer=open(sentencefilepath,"wb+")
    
    fileStr=file.read()    
    delimeterList=['.','"','(',')','?','!',',','{','}','[',']','*','-','/',';','`','~','@','$','%','^','&','*','+','*','/','\\','|','<','>',':','_','\'',' ']
    
    fileStr=fileStr.replace("...",".")
    fileStr=fileStr.replace(".",". ")
    #Get the first index of : =which will be treated as a segment
    #index=fileStr.find(':')
    #print index
    ##get the string from first index to segment index
    #if(index>=0):
        #segmentstring=fileStr[0:index]
        #tempSegmentString=segmentstring
        ##Get the len of the segment string (Not considering )
        #segmentStrLen=getSentenceLength(tempSegmentString);
        #if(segmentStrLen<=5):
            ##We are sure it is metadata,we will preserve the string in another file
            #segmentfilePointer.write(segmentstring)
            #segmentfilePointer.close()
            #fileStr=fileStr[index+1:]
        
    
    
    
    delimeterList=['?','.','!']
    #sentenceList=re.split(r'[?.!]', fileStr)
    #sentenceList=fileStr.split(delimeterList)
    #Sentence Tokennize Operation
    sentenceList = sent_tokenize(fileStr.strip())
    indextobeIgnored=[]
    for index,sentence in enumerate(sentenceList):
        print index
        if(index in indextobeIgnored):
            print indextobeIgnored
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
                if(tobemergeStatus==True):
                    nextsentence=str(sentenceList[index+count])
                
                    countDotCharacterNext=nextsentence.count(".")
                    sentence=sentence+nextsentence
                    nextindex=index+count
                    indextobeIgnored.append(nextindex)
                    print nextsentence+"::"+str(nextindex)+"::"+str(countDotCharacterNext)
                    print("\n")
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
        wordlengthStr="Word Strength::"+str(sentenceStrLen)
        sentence=sentence.replace(". ",".")
        sentencefilePointer.write(sentence)
        sentencefilePointer.write("\n")
        #sentencefilePointer.write("\n")
        sentencefilePointer.write(wordlengthStr)
        sentencefilePointer.write("\n")
        sentencefilePointer.write("\n")
        sentencefilePointer.write("\n")
    sentencefilePointer.close()
    segmentfilePointer.close()
    print("All Done")