import io
import re
import math
from statistics import median
import pymorphy2
from chardet import UniversalDetector
from os import listdir
from os.path import join, basename, isdir
from GetFitch import GetFitch

class SubsReader:
    def __init__(self, fileName, morph):
        self.__listOfTexts = None
        self.__fileName = fileName
        self.__morph = morph
        self.__sentArrTeget = None
        self.__sentArrNotTeget = None

    def __fileEncoding__(self, filename):
        detector = UniversalDetector()
        with open(filename, 'rb') as fh:
            for line in fh:
                detector.feed(line)
                if detector.done:
                    break
        detector.close()
        return detector.result['encoding']

    def __cleaningLine__(self, line):
        clearLine = re.sub('icq#\d+|#+|\{\\a6\}|\{\\an8\}'
                           '|<i>|</i>|\d+:\d+:\d+,\d+ --> \d+:\d+:\d+,\d+'
                           '|\n+|\r+|^\d+|^\.+$|\{\\fad\d+\}|\*+|<b>', '', line)
        if clearLine and clearLine != ' ':
            clearLine = re.sub('https?:\/\/.*[\r\n]*', '', clearLine, flags=re.MULTILINE)
            clearLine = re.sub('www\.\w+\.\w+', '', clearLine, flags=re.MULTILINE)
            clearLine = re.sub('\w+\.ru', '', clearLine, flags=re.MULTILINE)
            clearLine = re.sub('([a-z0-9_-]+\.)*[a-z0-9_-]+@[a-z0-9_-]+'
                               '(\.[a-z0-9_-]+)*\.[a-z]{2,6}', '', clearLine, flags=re.MULTILINE)
            clearLine = re.sub('"|\[|\]|\(|\)|<font color=#\d+\w+>|</font>|/|<font color=#\d+>', '', clearLine)
            clearLine = re.sub('\s*-\s|\s-\s*', ' ', clearLine)
            clearLine = re.sub('\.\.+|^\.\.+', '...', clearLine)
            clearLine = re.sub('\.\.\.$|\?!|!\?|\.{3}\?|\.{3}!', '.', clearLine)
            clearLine = re.sub('^\.+$|<i>', '', clearLine)
            clearLine = re.sub('"|\[|\]|\(|\)|<font color=#\d+\w+>|</font>|/|<font color=#\d+>', '', clearLine)
            clearLine = re.sub('"|\[|\]|\(|\)|<font color=\w+\d+>|</font>|/|<font color=#\d+>', '', clearLine)
            clearLine = re.sub('♪', '', clearLine)
            clearLine = re.sub('♪', '', clearLine)
            clearLine = re.sub('\{\\a6\}|\{\\fad\d+\}', '', clearLine)
            clearLine = re.sub('\$+', '', clearLine)
            clearLine = re.sub('%+', '', clearLine)
            clearLine = re.sub('\^+', '', clearLine)
            clearLine = re.sub('@+', '', clearLine)
            clearLine = re.sub('«+', '', clearLine)
            clearLine = clearLine.strip()
            return clearLine
        return ''

    def __cleaningWord__(self, word):
        word = (re.sub('[\.\?!,:]|#|\{\\an8\}|\.{3}|', '', word)).strip()
        word = (re.sub('{\\a6\}', '', word)).strip()
        word = (re.sub('…|^–|–$', '', word)).strip()
        word = (re.sub('^–+', '', word)).strip()
        word = (re.sub('-+$', '', word)).strip()
        word = (re.sub('»+', '', word)).strip()
        word = (re.sub('«+ ', '', word)).strip()
        word = (re.sub('^-+', '', word)).strip()
        word = (re.sub('–+$', '', word)).strip()
        return word

    def __cleanWord__(self, word, arr):
        word =  self.__cleaningWord__(word)
        if word:
            arr.append(word.lower())
        return arr

    def __morphParseWithPyMorphy__(self, morph, word):
        p = morph.parse(word)[0]
        tag = p.tag.POS
        if tag is None:
            tag = str(p.tag).split(',')[0]
        normiliseWord = p.normal_form
        return normiliseWord + '_' + tag

    def __cleanWordWithTags__(self, word, arr, morph):
        word = self.__cleaningWord__(word)
        if word:
            arr.append(self.__morphParseWithPyMorphy__(morph, word.lower()))
        return arr

    def __makeTaggetAndNotTeget__(self, fileName, morph):
        with open(fileName, encoding=self.__fileEncoding__(fileName), errors='ignore') as file:
            teggetSentArr = []
            notTeggitSentArr = []
            oneSentArrTegget = []
            oneSentArrNotTegget = []
            for line in file:
                clearLine = self.__cleaningLine__(line)
                if clearLine:
                    wordArray = clearLine.split()
                    for i in range(len(wordArray)):
                        if i == 0 and wordArray[i][0].isupper():
                            if oneSentArrTegget:
                                teggetSentArr.append(' '.join(oneSentArrTegget))
                                oneSentArrTegget.clear()
                            oneSentArrTegget = self.__cleanWordWithTags__(wordArray[i], oneSentArrTegget, morph)
                            oneSentArrNotTegget = self.__cleanWord__(wordArray[i], oneSentArrNotTegget)
                        elif (re.findall('\.$|\?$|!$', wordArray[i])
                            and not re.findall('\.{3}$', wordArray[i])):
                            oneSentArrTegget = self.__cleanWordWithTags__(wordArray[i], oneSentArrTegget, morph)
                            oneSentArrNotTegget = self.__cleanWord__(wordArray[i], oneSentArrNotTegget)
                            teggetSentArr.append(' '.join(oneSentArrTegget))
                            notTeggitSentArr.append(' '.join(oneSentArrNotTegget))
                            oneSentArrTegget.clear()
                            oneSentArrNotTegget.clear()
                        elif (i < len(wordArray) - 1
                            and re.findall('\.{3}$', wordArray[i])
                            and wordArray[i + 1][0].isupper()
                        ):
                            oneSentArrTegget = self.__cleanWordWithTags__(wordArray[i], oneSentArrTegget, morph)
                            oneSentArrNotTegget = self.__cleanWord__(wordArray[i], oneSentArrNotTegget)
                            teggetSentArr.append(' '.join(oneSentArrTegget))
                            notTeggitSentArr.append(' '.join(oneSentArrNotTegget))
                            oneSentArrTegget.clear()
                            oneSentArrNotTegget.clear()
                        else:
                            oneSentArrTegget = self.__cleanWordWithTags__(wordArray[i], oneSentArrTegget, morph)
                            oneSentArrNotTegget = self.__cleanWord__(wordArray[i], oneSentArrNotTegget)
            else:
                if oneSentArrTegget:
                    teggetSentArr.append(' '.join(oneSentArrTegget))
                    notTeggitSentArr.append(' '.join(oneSentArrNotTegget))
        return teggetSentArr, notTeggitSentArr

    @property
    def tegetSent(self):
        if self.__sentArrTeget is None:
            self.__sentArrTeget, self.__sentArrNotTeget = \
                self.__makeTaggetAndNotTeget__(self.__fileName, self.__morph)
        return self.__sentArrTeget

    @property
    def notTegetSent(self):
        if self.__sentArrNotTeget is None:
            self.__sentArrTeget, self.__sentArrNotTeget = \
                self.__makeTaggetAndNotTeget__(self.__fileName, self.__morph)
        return self.__sentArrNotTeget


class MakeSeria(SubsReader, GetFitch):
    def __init__(self, wayToSer, morph=None):
        self.__morph = morph
        if self.__morph is None:
            self.__morph = pymorphy2.MorphAnalyzer()
        SubsReader.__init__(self, wayToSer, morph)
        GetFitch.__init__(self, self.tegetSent, self.notTegetSent)
        self.__serName = basename(wayToSer).replace('.srt', '').replace('_', ' ')
        norm = re.sub(r'[^\w\s]+', r' ', self.__serName).strip()
        self.__serName = norm
        self.__allDict = None
        self.__tf = None
        self.__simpleSeriaArray = None

    def __str__(self):
        return self.__serName

    def __normilisedSeria__(self):
        pass

    def __sortDict__(self, myDict):
        sortDict = {}
        sortDict.update(dict(sorted(myDict.items(), key=lambda x: x[1], reverse=True)))
        return sortDict

    def __tf__(self, textArr):
        wordDic = {}
        wordArr = ' '.join(textArr).split()
        for it in wordArr:
            if it in wordDic:
                wordDic[it] = wordDic[it] + 1
            else:
                wordDic[it] = 1
        return wordDic

    @property
    def tf(self):
        if self.__tf is None:
            self.__tf = self.__tf__(self.tegetSent)
        return self.__tf

    @property
    def serName(self):
        return self.__serName

    @property
    def seriaInfo(self):
        allDict = {}
        allDict['seria_name'] = self.serName
        allDict.update(self.fitch)
        allDict['tf'] = self.tf
        allDict['raw_sent'] = self.notTegetSent
        allDict['raw_tegget'] = self.tegetSent
        return allDict

class MakeSeason:
    def __init__(self, wayToSeason, morph=None):
        self.__morph = morph
        if self.__morph is None:
            self.__morph = pymorphy2.MorphAnalyzer()
        self.__wayToSeason = wayToSeason
        self.__seasName = basename(self.__wayToSeason)
        self.__serList = None
        self.__medFitch = None
        self.__medTf = None
        self.__simpIDF = None

    def __readSerias__(self, wayToSeas):
        serialsList = []
        files = listdir(wayToSeas)
        for file in files:
            if file.endswith('.srt'):
                serialsList.append(MakeSeria(join(wayToSeas, file), self.__morph))
        return serialsList

    def __seasNotNormaliseIdf__(self, serList):
        korpDic = {}
        for ser in serList:
            temporarDict = {}
            for term in ' '.join(ser.tegetSent).split():
                if term not in temporarDict:
                    if term in korpDic:
                        korpDic[term] = korpDic[term] + 1
                    else:
                        korpDic[term] = 1
                    temporarDict[term] = 1
        for key in korpDic:
            korpDic[key] = korpDic[key]
        return korpDic

    def __medTf__(self, serList):
        medTfDict = {}
        for ser in serList:
            for term in ser.tf:
                if term not in medTfDict:
                    medTfDict[term] = [ser.tf[term]]
                else:
                    medTfDict[term].append(ser.tf[term])
        for it in medTfDict:
            medTfDict[it] = median(medTfDict[it])
        return medTfDict

    def __medFitch__(self, serList):
        medFitch = {}
        for ser in serList:
            for fitch in ser.fitch:
                if fitch not in medFitch:
                    medFitch[fitch] = [ser.fitch[fitch]]
                else:
                    medFitch[fitch].append(ser.fitch[fitch])
        for it in medFitch:
            medFitch[it] = median(medFitch[it])
        return medFitch

    @property
    def serList(self):
        if self.__serList is None:
            self.__serList = self.__readSerias__(self.__wayToSeason)
        return self.__serList

    @property
    def seasName(self):
        return self.__seasName

    @property
    def fitch(self):
        if self.__medFitch is None:
            self.__medFitch = self.__medFitch__(self.serList)
        return self.__medFitch

    @property
    def tf(self):
        if self.__medTf is None:
            self.__medTf = self.__medTf__(self.serList)
        return self.__medTf

    @property
    def idf(self):
        if self.__simpIDF is None:
            self.__simpIDF = self.__seasNotNormaliseIdf__(self.serList)
        return self.__simpIDF

    @property
    def seasLen(self):
        return len(self.serList)

    @property
    def seasInfo(self):
        allDict = {}
        allDict['season_name'] = self.seasName
        allDict.update(self.fitch)
        allDict['tf'] = self.tf
        allDict['idf'] = self.idf
        return allDict


class MakeSerial:
    def __init__(self, wayToSerial, morph=None):
        self.__morph = morph
        if self.__morph is None:
            self.__morph = pymorphy2.MorphAnalyzer()
        self.__wayToSerial = wayToSerial
        self.__serialName = basename(self.__wayToSerial).replace('_', ' ')
        self.__seasList = None
        self.__medFitch = None
        self.__medTf = None
        self.__idf = None
        self.__tfIdf = None

    def __readSeasons__(self, wayToSerial):
        serialsList = []
        files = listdir(wayToSerial)
        for file in files:
            if isdir(join(wayToSerial, file)):
                serialsList.append(MakeSeason(join(wayToSerial, file), self.__morph))
        return serialsList

    def __idf__(self, seasList):
        korpDic = {}
        serLen = 0
        for seas in seasList:
            serLen += seas.seasLen
            for it in seas.idf:
                if it in korpDic:
                    korpDic[it] = korpDic[it] + seas.idf[it]
                else:
                    korpDic[it] = seas.idf[it]
        for key in korpDic:
            korpDic[key] = math.log2(serLen / korpDic[key])
        return korpDic

    def __medTf__(self, seasList):
        medTfDict = {}
        for season in seasList:
            for term in season.tf:
                if term not in medTfDict:
                    medTfDict[term] = [season.tf[term]]
                else:
                    medTfDict[term].append(season.tf[term])
        for it in medTfDict:
            medTfDict[it] = median(medTfDict[it])
        return medTfDict

    def __medFitch__(self, seasList):
        medFitch = {}
        for season in seasList:
            for fitch in season.fitch:
                if fitch not in medFitch:
                    medFitch[fitch] = [season.fitch[fitch]]
                else:
                    medFitch[fitch].append(season.fitch[fitch])
        for it in medFitch:
            medFitch[it] = median(medFitch[it])
        return medFitch

    def __tfIdf__(self, tf, idf):
        tfIdfDict = {}
        for it in idf:
            tfIdfDict[it] = tf[it] * idf[it]
        return tfIdfDict

    @property
    def seasonsList(self):
        if self.__seasList is None:
            self.__seasList = self.__readSeasons__(self.__wayToSerial)
        return self.__seasList

    @property
    def serialName(self):
        return self.__serialName

    @property
    def fitch(self):
        if self.__medFitch is None:
            self.__medFitch = self.__medFitch__(self.seasonsList)
        return self.__medFitch

    @property
    def tf(self):
        if self.__medTf is None:
            self.__medTf = self.__medTf__(self.seasonsList)
        return self.__medTf

    @property
    def idf(self):
        if self.__idf is None:
            self.__idf = self.__idf__(self.seasonsList)
        return self.__idf

    @property
    def tfIdf(self):
        if self.__tfIdf is None:
            self.__tfIdf = self.__tfIdf__(self.tf, self.idf)
        return self.__tfIdf

    @property
    def serialLen(self):
        return len(self.seasonsList)

    @property
    def serialInfo(self):
        allDict = {}
        allDict['serial_name'] = self.serialName
        allDict.update(self.fitch)
        allDict['tf'] = self.tf
        allDict['idf'] = self.idf
        allDict['tf_idf'] = self.tfIdf
        return allDict
