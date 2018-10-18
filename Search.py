import os,sys
import timeit
from bisect import bisect
from math import log10
from stemming.porter import stem
import re
from collections import defaultdict
from operator import itemgetter
import timeit

docTitleMap = dict()
noDocs = 0
try:
    f = open("docTitMap.txt","r")
    for line in f:
        docID, titleMap = line.split("#")
        docTitleMap[docID] = titleMap
        noDocs += 1
except:
    print "Can't find the Title and Document ID Mapping File. (docTitleMap.txt)."
    print "Re - run the program when the file is in the same folder."
    sys.exit(1)

secondaryIndex = list()
try:
    f = open("finalIndex/secondaryIndex.txt","r")
    for line in f:
        secondaryIndex.append(line.split()[0])
except:
    print "Can't find the secondary index file in 'finalIndex' Folder."
    print "Re - run the program when the file is in the same folder."
    sys.exit(1)

stopWords = set()
try:
    f = open("stopwords.txt","r")
    for line in f:
        stopWords.add(line.strip())
except:
    print "Can't find the List of Stopwords File. (stopwords.txt)."
    print "Re - run the program when the file is in the same folder."
    sys.exit(1)
    
def queryNormal(queryWords):
    wordsToSearch = list()
    for word in queryWords:
        word = word.lower().strip()
        if word not in stopWords:
            word = stem(word)
        if word.isalpha() and len(word)>=3 and word not in stopWords:
            wordsToSearch.append(word)
    globalSearch = dict(list())
    for word in wordsToSearch:
        loc = bisect(secondaryIndex,word)
        startFlag = False
        if loc-1 >= 0 and secondaryIndex[loc-1] == word:
            startFlag = True
            if loc-1 != 0:
                loc -= 1
            if loc+1 == len(secondaryIndex) and secondaryIndex[loc] == word:
                loc += 1
        primaryFile = "finalIndex/index" + str(loc) + ".txt"
        file = open(primaryFile,"r")
        data = file.read()
        if startFlag:
            startIndex = data.find(word+"=")
        else:
            startIndex = data.find("\n"+word+"=")
        endIndex = data.find("\n",startIndex+1)
        reqLine = data[startIndex:endIndex]
        pl = reqLine.split("=")[1].split(",")
        numDoc = len(pl)
        idf = log10(noDocs/numDoc)
        for i in pl:
            docID, entry = i.split(":")
            if docID in globalSearch:
                globalSearch[docID].append(entry+"_"+str(idf))
            else:
                globalSearch[docID] = [entry+"_"+str(idf)]
    lengthFreq = dict(dict())
    regEx = re.compile(r'(\d+|\s+)')
    for k in globalSearch:
        weightedFreq = 0
        n = len(globalSearch[k])
        for x in globalSearch[k]:
            x,idf = x.split("_")
            x = x.split("#")
            for y in x:
                lis = regEx.split(y)
                tagType, freq = lis[0], lis[1]
                if tagType == "t":
                    weightedFreq += int(freq)*1000
                elif tagType == "i" or tagType == "c" or tagType == "r" or tagType == "e":
                    weightedFreq += int(freq)*50
                elif tagType == "b":
                    weightedFreq += int(freq)
        if n in lengthFreq:
            lengthFreq[n][k] = float(log10(1+weightedFreq))*float(idf)
        else:
            lengthFreq[n] = {k : float(log10(1+weightedFreq))*float(idf)}
    count = 0
    flag = False
    # resultList = []
    K = 10
    for k,v in sorted(lengthFreq.items(),reverse=True):
        for k1,v1 in sorted(v.items(),key=itemgetter(1),reverse=True):
            print docTitleMap[k1]
            count += 1
            if count == K:
                flag = True
                break
        if flag:
            break
        
def queryField(queryWords):
    wordsToSearch = list()
    fieldDict = dict()
    for word in queryWords:
        tag, w = word.split(":")
        w = w.lower()
        if w not in stopWords:
            w = stem(w)
        if w.isalpha() and len(w)>=3 and w not in stopWords:
            wordsToSearch.append(w)
            if w in fieldDict:
                fieldDict[w] += tag
            else:
                fieldDict[w] = tag
    globalSearch = dict(list())
    for word in wordsToSearch:
        loc = bisect(secondaryIndex,word)
        startFlag = False
        if loc-1>0 and secondaryIndex[loc-1] == word:
            startFlag = True
            if loc-1 != 0:
                loc -= 1
            if loc+1 == len(secondaryIndex) and secondaryIndex[loc] == word:
                loc += 1
        primaryFile = "finalIndex/index" + str(loc) + ".txt"
        file = open(primaryFile,"r")
        data = file.read()
        if startFlag:
            startIndex = data.find(word+"=")
        else:
            startIndex = data.find("\n"+word+"=")
        endIndex = data.find("\n",startIndex+1)
        reqLine = data[startIndex:endIndex]
        pl = reqLine.split("=")[1].split(",")
        numDoc = len(pl)
        idf = log10(noDocs/numDoc)
        for i in pl:
            docID, entry = i.split(":")
            if docID in globalSearch:
                globalSearch[docID].append(entry+"_"+str(idf))
            else:
                globalSearch[docID] = [entry+"_"+str(idf)]
    lengthFreq = dict(dict())
    regEx = re.compile(r'(\d+|\s+)')
    for k in globalSearch:
        weightedFreq = 0
        n = len(globalSearch[k])
        for x in globalSearch[k]:
            x,idf = x.split("_")
            x = x.split("#")
            for y in x:
                lis = regEx.split(y)
                tagType, freq = lis[0], lis[1]
                if tagType == "t":
                    weightedFreq += int(freq)*1000
                elif tagType == "i" or tagType == "c" or tagType == "r" or tagType == "e":
                    weightedFreq += int(freq)*50
                elif tagType == "b":
                    weightedFreq += int(freq)
        if n in lengthFreq:
            lengthFreq[n][k] = float(log10(1+weightedFreq))*float(idf)
        else:
            lengthFreq[n] = {k : float(log10(1+weightedFreq))*float(idf)}
    count = 0
    flag = False
    # resultList = []
    K = 10
    for k,v in sorted(lengthFreq.items(),reverse=True):
        for k1,v1 in sorted(v.items(),key=itemgetter(1),reverse=True):
            print docTitleMap[k1]
            count += 1
            if count == K:
                flag = True
                break
        if flag:
            break

while True:
    query = raw_input("Enter your query: ")
    start = timeit.default_timer()
    queryType = ""
    if ":" in query:
        queryType = "F"
    else:
        queryType = "N"
    queryWords = query.split()
    if queryType == "N":
        try:
            queryNormal(queryWords)
            stop = timeit.default_timer()
            print "Query Took ",stop-start," seconds."
        except:
            print "Some Error Occurred! Try Again"
    else:
        try:
            queryField(queryWords)
            stop = timeit.default_timer()
            print "Query Took ",stop-start," seconds."
        except:
            print "Some Error Occurred! Try Again"
