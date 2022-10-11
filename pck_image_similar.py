import os
import os.path
import shutil
import configparser
import logging
import sys

imgSourceDirectory=""
imgProcessedDirectory=""
imgMatchFileOrDirectory=""
imgControlDirectory=""
processMode=""
processBatchCounts=[]
shouldIncludeNonExistedFiles=True
SKIP_SYSTEM_FILENAME=".DS_Store"

doLoadAndIndex=True
#doIndex=True
doSearchAndProcess=True
KEY_ARGV_SKIP_STEP="-s"
KEY_ARGV_SKIP_LOAD="L"
#KEY_ARGV_SKIP_INDEX="I"
KEY_ARGV_SKIP_SEARCH="S"
KEY_ARGV_MATCH_FILEPATH="-m"

myLog=logging.getLogger("myLogger") 
hdlr=logging.StreamHandler()
logDirname = "logs"
if not os.path.exists(logDirname):
    os.makedirs(logDirname)
logFilename = logDirname + "/log.txt"
fhdlr=logging.FileHandler(logFilename)
myLog.addHandler(hdlr)
myLog.addHandler(fhdlr)
myLog.setLevel(logging.DEBUG)

def parseArgv():
    global doLoadAndIndex, doSearchAndProcess, imgMatchFileOrDirectory
    for i in range(len(sys.argv)):
        if i == 0:
            continue
        anArgv = sys.argv[i]
        if anArgv[0:2] == KEY_ARGV_SKIP_STEP:
            anArgvRest = anArgv[2:]
            for i in range(len(anArgvRest)):
                aChar = anArgvRest[i]
                if aChar == KEY_ARGV_SKIP_LOAD:
                    doLoadAndIndex = False
                #elif aChar == KEY_ARGV_SKIP_INDEX:
                #    doIndex = False
                elif aChar == KEY_ARGV_SKIP_SEARCH:
                    doSearchAndProcess = False
        if anArgv[0:2] == KEY_ARGV_MATCH_FILEPATH:
            nextArgv = sys.argv[i+1]
            imgMatchFileOrDirectory = nextArgv
                
def parseConfigs():
    parser = configparser.ConfigParser()
    parser.read("config.txt")
    global imgSourceDirectory, imgProcessedDirectory, imgMatchFileOrDirectory, imgControlDirectory, processMode, processBatchCounts, shouldIncludeNonExistedFiles
    imgSourceDirectory = parser.get("DEFAULT", "imgSourceDirectory")
    imgProcessedDirectory = parser.get("DEFAULT", "imgProcessedDirectory")
    if len(imgMatchFileOrDirectory) == 0:
        imgMatchFileOrDirectory = parser.get("DEFAULT", "imgMatchFileOrDirectory")
    imgControlDirectory = parser.get("DEFAULT", "imgControlDirectory")
    matchPattern = parser.get("DEFAULT", "matchPattern")
    processMode = parser.get("DEFAULT", "processMode")
    shouldIncludeNonExistedFilesStr = parser.get("DEFAULT", "shouldIncludeNonExistedFiles")
    shouldIncludeNonExistedFiles = not (shouldIncludeNonExistedFilesStr == "false")

    myLog.debug("parseConfigs: imgSourceDirectory:"+imgSourceDirectory+";")
    myLog.debug("parseConfigs: imgProcessedDirectory:"+imgProcessedDirectory+";")
    myLog.debug("parseConfigs: imgMatchFileOrDirectory:"+imgMatchFileOrDirectory+";")
    myLog.debug("parseConfigs: imgControlDirectory:"+imgControlDirectory+";")
    myLog.debug("parseConfigs: matchPattern:"+matchPattern+";")
    myLog.debug("parseConfigs: processMode:"+processMode+";")
    myLog.debug("parseConfigs: shouldIncludeNonExistedFiles:"+str(shouldIncludeNonExistedFiles)+";")

    processBatchCountsStr = matchPattern.split(",")
    processBatchCounts = list(map(int, processBatchCountsStr))

def processMatchFileOrDirectory():
    myLog.debug("processMatchFileOrDirectory: START;")

    global imgMatchFilePathList, imgMatchFileOrDirectory
    imgMatchFilePathList = []
    if os.path.isdir(imgMatchFileOrDirectory):
        # TODO to be further developed, not all cases below are supported for now
        # 1 - a directory with only 1 file within
        # 2 - a directory with multiple files within
        # 3 - a directory with multiple sub-directories, each with 1 file within
        # if imgMatchFileOrDirectory is directory, recursive run searching on each file within
        for aFileOrDirectory in os.listdir(imgMatchFileOrDirectory):
            aFileOrDirectoryFullPath = os.path.join(imgMatchFileOrDirectory, aFileOrDirectory)
            
            if os.path.isdir(aFileOrDirectoryFullPath):
                # TODO TBC - not handling sub-directories for now
                myLog.debug("processMatchFileOrDirectory: found subdirectory [" + aFileOrDirectoryFullPath + "], will skip for now...")
            else:
                if SKIP_SYSTEM_FILENAME in aFileOrDirectoryFullPath:
                    myLog.debug("processMatchFileOrDirectory: found system file [" + SKIP_SYSTEM_FILENAME + "], skipping...")
                else:
                    myLog.debug("processMatchFileOrDirectory: found file [" + aFileOrDirectoryFullPath + "]; will add to imgMatchFilePathList")
                    imgMatchFilePathList.append(aFileOrDirectoryFullPath)
            
    else:
        # if imgMatchFileOrDirectory is file, single run searching on that file        
        if not os.path.exists(imgMatchFileOrDirectory):
            myLog.debug("processMatchFileOrDirectory: file [" + imgMatchFileOrDirectory + "] not existed, skipping...") 
        else:    
            imgMatchFileOrDirectory = os.path.abspath(imgMatchFileOrDirectory)
            myLog.debug("processMatchFileOrDirectory: found file [" + imgMatchFileOrDirectory + "], will use this for imgMatchFileOrDirectory;")
            imgMatchFilePathList.append(imgMatchFileOrDirectory)    
    imgMatchFilePathList.sort()
    myLog.debug("processMatchFileOrDirectory: END, len(imgMatchFilePathList):" + str(len(imgMatchFilePathList)) + ";")
            

def load():
    myLog.debug("load: START;")
    from DeepImageSearch import LoadData
    import ssl
    ssl._create_default_https_context = ssl._create_unverified_context
    global imgList

    allImgDirectorySet = set()
    allImgDirectorySet.add(imgSourceDirectory)
    if (len(imgControlDirectory) > 0):
        allImgDirectorySet.add(imgControlDirectory)
    for aListEntry in imgMatchFilePathList:
        allImgDirectorySet.add(os.path.dirname(aListEntry))

    allImgDirectoryList = list(allImgDirectorySet)

    myLog.debug("load: len(allImgDirectoryList):" + str(len(allImgDirectoryList)) + ";")
    for aDirectory in allImgDirectoryList:
        myLog.debug("load: aDirectory:[" + aDirectory + "];")
    imgList = LoadData().from_folder(allImgDirectoryList)
    myLog.debug("load: LoadData() DONE; len(imgList):" + str(len(imgList)) + ";")

def index():
    myLog.debug("index: START;")
    from DeepImageSearch import Index
    Index(imgList).Start()
    myLog.debug("index: Index() DONE;")

def searchAndProcess():
    from DeepImageSearch import SearchImage
    myLog.debug("searchAndProcess: START;")

    for aMatchFilePath in imgMatchFilePathList:
        imgProcessedSet = set()
        imgMatchedSet = set()
        if (imgSourceDirectory not in aMatchFilePath):
            imgMatchedSet.add(aMatchFilePath)
        # run a full processBatchCounts once, for each aMatchFilePath
        aMatchFilenameWithExtension = os.path.basename(aMatchFilePath)
        aMatchFilename = os.path.splitext(aMatchFilenameWithExtension)[0]
        for numToProcessThisBatch in processBatchCounts:
            numToProcessUpToThisBatch = len(imgProcessedSet) + numToProcessThisBatch
            imgProcessedDirname = imgProcessedDirectory + "/" + aMatchFilename + "/" + str(numToProcessUpToThisBatch) + "/"
            myLog.debug("__numToProcessThisBatch:" + str(numToProcessThisBatch) + "; numToProcessUpToThisBatch:" + str(numToProcessUpToThisBatch) + "; imgProcessedDirname:" + imgProcessedDirname + ";")
            if not os.path.exists(imgProcessedDirname):
                os.makedirs(imgProcessedDirname)

            while len(imgProcessedSet) < numToProcessUpToThisBatch:
                numToSearchThisRound = numToProcessUpToThisBatch - len(imgProcessedSet) + len(imgMatchedSet)
                myLog.debug("____numToSearchThisRound:" + str(numToSearchThisRound) + "; len(imgProcessedSet):" + str(len(imgProcessedSet)) + "; len(imgMatchedSet):" + str(len(imgMatchedSet)) + ";")
                imgSimilarDict = SearchImage().get_similar_images(image_path = aMatchFilePath, number_of_images = numToSearchThisRound)
                
                for imgSimilarFilepath in imgSimilarDict.values():
                    # skip all matched file (i.e. already in imgMatchedSet)
                    if imgSimilarFilepath in imgMatchedSet:
                        #print("______file [" + imgSimilarFilepath + "] is matched already, skipping...")
                        continue
                    # always add to imgMatchedSet
                    imgMatchedSet.add(imgSimilarFilepath)
                    # skip all files not under imgSourceDirectory
                    if imgSourceDirectory not in imgSimilarFilepath:
                        #print("______file [" + imgSimilarFilepath + "] is not under imgSourceDirectory, skipping...")
                        continue

                    imgProcessedFilepath = imgProcessedDirname + os.path.basename(imgSimilarFilepath)
                    if os.path.exists(imgSimilarFilepath):
                        if processMode == "move":
                            #print("searchAndProcess: move file from [" + imgSimilarFilepath + "] to [" + imgProcessedFilepath + "]")
                            shutil.move(imgSimilarFilepath, imgProcessedFilepath)
                        else:
                            #print("searchAndProcess: copy file from [" + imgSimilarFilepath + "] to [" + imgProcessedFilepath + "]")
                            shutil.copy2(imgSimilarFilepath, imgProcessedFilepath)
                        imgProcessedSet.add(imgSimilarFilepath)
                    else:
                        if shouldIncludeNonExistedFiles:
                            imgProcessedSet.add(imgSimilarFilepath)
                    if len(imgProcessedSet) >= numToProcessUpToThisBatch:
                        break
    myLog.debug("searchAndProcess: DONE; len(imgProcessedSet):" + str(len(imgProcessedSet)) + "; len(imgMatchedSet):" + str(len(imgMatchedSet)) + ";")


myLog.debug("pck_image_similar: START; v1.0;")

parseArgv()

parseConfigs()

processMatchFileOrDirectory()

if not doLoadAndIndex:
    myLog.debug("pck_image_similar: doLoadAndIndex is false, skipping here...")
else:
    load()
    index()

if not doSearchAndProcess:
    myLog.debug("pck_image_similar: doSearchAndProcess is false, skipping here...")
else:
    searchAndProcess()

myLog.debug("pck_image_similar: END;")
