import os,sys
import timeit
import glob
from collections import defaultdict
from heapq import heapify, heappush, heappop

folderToStore = "finalIndex/"
indexFileCount = 0
secondaryIndex = dict()
chunkSize = 100000

indexFiles = glob.glob("./indexFiles/*")
primaryIndex = open("primaryIndex.txt","w")
completedFiles = [0] * len(indexFiles)
filePointers = dict()
currentRowOfFile = dict()
percolator = list()
words = dict()
total = 0
invertedIndex = defaultdict()

def writeToPrimary():
	offset = []
	firstWord = True
	indexFileCount += 1
	fileName = folderToStore + "index" + str(indexFileCount) + ".txt"
	fp = open(fileName,"w")
	for i in sorted(invertedIndex):
		if firstWord:
			secondaryIndex[i] = indexFileCount
			firstWord = False
		toWrite = str(i) + "=" + invertedIndex[i] + "\n"
		fp.write(toWrite)

def writeToSecondary():
	fileName = folderToStore + "secondaryIndex.txt"
	fp = open(fileName,"w")
	for i in sorted(secondaryIndex):
		toWrite = str(i) + " " + str(secondaryIndex[i]) + "\n"
		fp.write(toWrite)

start = timeit.default_timer()


fileCount = 0
for i in xrange(len(indexFiles)):
	completedFiles[i] = 1
	try:
		filePointers[i] = open(indexFiles[i],"r")
		fileCount += 1
	except:
		print "Could Open Files: ",fileCount
	currentRowOfFile[i] = filePointers[i].readline()
	words[i] = currentRowOfFile[i].strip().split("=")
	if words[i][0] not in percolator:
		heappush(percolator,words[i][0])

while True:
	if completedFiles.count(0) == len(indexFiles):
		break
	else:
		total += 1
		word = heappop(percolator)
		for i in xrange(len(indexFiles)):
			if completedFiles[i] and words[i][0] == word:
				if word in invertedIndex:
					invertedIndex[word] += "," + words[i][1]
				else:
					invertedIndex[word] = words[i][1]

				if total == chunkSize:
					total = 0
					writeToPrimary()
					invertedIndex.clear()

				currentRowOfFile[i] = filePointers[i].readline().strip()

				if currentRowOfFile[i]:
					words[i] = currentRowOfFile[i].split("=")
					if words[i][0] not in percolator:
						heappush(percolator,words[i][0])
				else:
					completedFiles[i] = 0
					filePointers[i].close()
					os.remove(indexFiles[i])

writeToPrimary()
writeToSecondary()
stop = timeit.default_timer()

print "Time for Merging:",stop-start," seconds."
mins = float(stop-start)/float(60)
print "Time for Merging:",mins," Minutes."
hrs = float(mins)/float(60)
print "Time for Merging:",hrs," Hours."
print "Check the External File(s) Now!"
