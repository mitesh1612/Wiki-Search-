from xml.sax import parse,ContentHandler
import re
from stemming.porter import stem
import timeit
import os
import sys
from collections import defaultdict

invertedIndex = defaultdict(lambda:defaultdict(lambda:defaultdict(int)))
indexFolder = "indexFiles/"
documentTitleMapping = open("docTitleMap.txt","w")
pushLimit = 4000
# Getting the StopWords
stopWords = set()
try:
	f = open("stopwords.txt","r")
	for line in f:
		line = line.strip()
		stopWords.add(line)
except:
	print "Can't find the List of Stopwords File. (stopwords.txt)."
	print "Re - run the program when the file is in the same folder."
	sys.exit(1)
# Regular Expression to remove URLs
regExp1 = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',re.DOTALL)
# Regular Expression to remove CSS
regExp2 = re.compile(r'{\|(.*?)\|}',re.DOTALL)
# Regular Expression to remove {{cite **}} or {{vcite **}}
regExp3 = re.compile(r'{{v?cite(.*?)}}',re.DOTALL)
# Regular Expression to remove Punctuation
regExp4 = re.compile(r'[.,;_()"/\']',re.DOTALL)
# Regular Expression to remove [[file:]]
regExp5 = re.compile(r'\[\[file:(.*?)\]\]',re.DOTALL)
# Regular Expression to remove Brackets and other meta characters from title
regExp6 = re.compile(r"[~`!@#$%-^*+{\[}\]\|\\<>/?]",re.DOTALL)
# Regular Expression for Categories
catRegExp = r'\[\[category:(.*?)\]\]'
# Regular Expression for Infobox
infoRegExp = r'{{infobox(.*?)}}'
# Regular Expression for References
refRegExp = r'== ?references ?==(.*?)=='
# Regular Expression to remove Infobox
regExp7 = re.compile(infoRegExp,re.DOTALL)
# Regular Expression to remove references
regExp8 = re.compile(refRegExp,re.DOTALL)
# Regular Expression to remove {{.*}} from text
regExp9 = re.compile(r'{{(.*?)}}',re.DOTALL)
# Regular Expression to remove <..> tags from text
regExp10 = re.compile(r'<(.*?)>',re.DOTALL)
# Regular Expression to remove junk from text
regExp11 = re.compile(r"[~`!@#$%-^*+{\[}\]\|\\<>/?]",re.DOTALL)

def cleanText(text):
    '''
    Use the Regular Expressions stored to remove unnecessary things from text for tokenizing
    '''
    text = regExp1.sub('',text)
    text = regExp2.sub('',text)
    text = regExp3.sub('',text)
    text = regExp4.sub(' ',text)
    text = regExp5.sub('',text)
    text = regExp10.sub('',text)
    return text

def addToIndex(wordList,docID,t):
    '''
    Removes all the non-ASCII words and then performs stemming and then adds in the index at appropriate location.
    '''
    for word in wordList:
        word = word.strip().encode('utf-8')
        if word.isalpha() and len(word)>3 and word not in stopWords:
            # Stemming the Words
            word = stem(word)
            if word not in stopWords:
                if word in invertedIndex:
                    if docID in invertedIndex[word]:
                    	if t in invertedIndex[word][docID]:
                    		invertedIndex[word][docID][t] += 1
                    	else:
                    		invertedIndex[word][docID][t] = 1
                    else:
                    	invertedIndex[word][docID] = {t:1}
                else:
                	invertedIndex[word] = dict({docID:{t:1}})
                    
def processBuffer(text,docID,titleFlag,textFlag):
    '''
	Takes the text from the parsing buffer.
	For title, it just tokenizes and adds to the title part of the document index.
	For text, it further searches for categories,references,infobox,external links and does processing accordingly.
	'''
    # Case Folding : Converting all to Lower Case
    text = text.lower()
    # Cleaning the text using Regular Expressions for tokenizing
    text = cleanText(text)
    if titleFlag:
        # Add to index for titles
        words = text.split()
        words = [regExp6.sub(' ',word) for word in words if word.isalpha() and word not in stopWords]
        addToIndex(words,docID,"t")
    elif textFlag:
        # Get different types of text and add to index respectively
        textContent = []
        infobox = []
        categories = []
        external = []
        references = []
        extInd = 0
        refInd = 0
        catInd = len(text)
        categories = re.findall(catRegExp,text,flags=re.MULTILINE)
        infobox = re.findall(infoRegExp,text,re.DOTALL)
        text = regExp7.sub('',text)
        try:
            extInd = text.index('=external links=')+20
        except:
            pass
        try:
            catInd = text.index('[[category:')+20
        except:
            pass
        if extInd:
            external = text[extInd:catInd]
            external = re.findall(r'\[(.*?)\]',external,flags=re.MULTILINE)
        references = re.findall(refRegExp,text,flags=re.DOTALL)
        if extInd:
            text = text[0:extInd-20]
        # Adding index for Text
        text = regExp8.sub('',text)
        text = regExp9.sub('',text)
        text = regExp11.sub(' ',text)
        words = text.split()
        addToIndex(words,docID,"b")
        # Adding index for categories
        categories = ' '.join(categories)
        categories = regExp11.sub(' ',categories)
        categories = categories.split()
        addToIndex(categories,docID,"c")
        # Adding index for External
        external = ' '.join(external)
        external = regExp11.sub(' ',external)
        external = external.split()
        addToIndex(external,docID,"e")
        # Adding index for References
        references = ' '.join(references)
        references = regExp11.sub(' ',references)
        references = references.split()
        addToIndex(references,docID,"r")
        # Adding index for Infobox
        for infoList in infobox:
            tokenList = []
            tokenList = re.findall(r'=(.*?)\|',infoList,re.DOTALL)
            tokenList = ' '.join(tokenList)
            tokenList = regExp11.sub(' ',tokenList)
            tokenList = tokenList.split()
            addToIndex(tokenList,docID,2)

        if docID%pushLimit == 0:
            f = open(indexFolder+str(docID)+".txt","w")
            for key,val in sorted(invertedIndex.items()):
            	s =str(key.encode('utf-8'))+"="
            	for k,v in sorted(val.items()):
            		s += str(k) + ":"
            		for k1,v1 in v.items():
            			s = s + str(k1) + str(v1) + "#"
            		s = s[:-1]+","
            	f.write(s[:-1]+"\n")
            f.close()
            invertedIndex.clear()
            print docID," Documents Processed..."	
            
class WikiDataHandler(ContentHandler):
    def __init__(self):
        self.docID = 0
        self.buffer = ""
        self.titleFlag = False
        self.textFlag = False
        self.flag = False
        self.pageTitle = ""
    
    def startElement(self,element,attributes):
        if element == "title":
            self.buffer = ""
            self.titleFlag = True
            self.flag = True
        if element == "page":
            self.docID += 1
        if element == "text":
            self.buffer = ""
            self.textFlag = True
       	if element == "id" and self.flag:
       		self.buffer = ""
    
    def endElement(self,element):
        if element == "title":
            processBuffer(self.buffer,self.docID,True,False)
            self.titleFlag = False
            self.pageTitle = self.buffer
            self.buffer = ""
        elif element == "text":
            processBuffer(self.buffer,self.docID,False,True)
            self.textFlag = False
            self.buffer = ""
        elif element == "id" and self.flag:
        	try:
        		documentTitleMapping.write(str(self.docID)+"#"+self.pageTitle+":"+self.buffer+"\n")
        	except:
        		documentTitleMapping.write(str(self.docID)+"#"+self.pageTitle.encode('utf-8')+":"+self.buffer.encode('utf-8')+"\n")
        	self.flag = False
        	self.buffer = ""

            
    def characters(self,content):
        self.buffer = self.buffer + content

if len(sys.argv) != 2:
	print "Incorrect Number of Command Line Arguments provided."
	print "Run using : ./index.sh <path-to-dump>"
	sys.exit(1)
# Parsing the dump and creating the index
print "Parsing the Dump."
start = timeit.default_timer()
print "Input File Given: ",sys.argv[1]
parse(sys.argv[1],WikiDataHandler())
stop = timeit.default_timer()
print "Time for Parsing:",stop-start," seconds."
mins = float(stop-start)/float(60)
print "Time for Parsing:",mins," Minutes."
hrs = float(mins)/float(60)
print "Time for Parsing:",hrs," Hours."
print "Check the External File(s) Now!"
