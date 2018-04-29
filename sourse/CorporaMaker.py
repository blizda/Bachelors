import io
import re
import os
import pymorphy2 as pymorphy2
from chardet import UniversalDetector

class SubsReader:
    def __init__(self, fileName, morph=None):
        self.__morph = morph
        if self.__morph is None:
            self.__morph = pymorphy2.MorphAnalyzer()
        self.__listOfTexts = None
        self.__fileName = fileName

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
        word = self.__cleaningWord__(word)
        if word:
            arr.append(word.lower())
        return arr

    def __justCleanWord__(self, word, arr):
        word = self.__cleaningWord__(word)
        if word:
            arr.append(word)
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

    def __readToSentArr__(self):
        with open(self.__fileName, encoding=self.__fileEncoding__(self.__fileName), errors='ignore') as file:
            sentArr = []
            oneSentArr = []
            for line in file:
                clearLine = self.__cleaningLine__(line)
                if clearLine:
                    wordArray = clearLine.split()
                    for i in range(len(wordArray)):
                        if i == 0 and wordArray[i][0].isupper():
                            if oneSentArr:
                                sentArr.append(' '.join(oneSentArr))
                                oneSentArr.clear()
                            oneSentArr = self.__cleanWord__(wordArray[i], oneSentArr)
                        elif (re.findall('\.$|\?$|!$', wordArray[i])
                              and not re.findall('\.{3}$', wordArray[i])):
                            oneSentArr = self.__cleanWord__(wordArray[i], oneSentArr)
                            sentArr.append(' '.join(oneSentArr))
                            oneSentArr.clear()
                        elif (i < len(wordArray) - 1
                              and re.findall('\.{3}$', wordArray[i])
                              and wordArray[i + 1][0].isupper()
                        ):
                            oneSentArr = self.__cleanWord__(wordArray[i], oneSentArr)
                            sentArr.append(' '.join(oneSentArr))
                            oneSentArr.clear()
                        else:
                            oneSentArr = self.__cleanWord__(wordArray[i], oneSentArr)
            else:
                if oneSentArr:
                    sentArr.append(' '.join(oneSentArr))
        return sentArr

    def __makeTaggetSentArrWithPyMorphy__(self, fileName, morph):
        with open(fileName, encoding=self.__fileEncoding__(fileName), errors='ignore') as file:
            sentArr = []
            oneSentArrTegget = []
            for line in file:
                clearLine = self.__cleaningLine__(line)
                if clearLine:
                    wordArray = clearLine.split()
                    for i in range(len(wordArray)):
                        if i == 0 and wordArray[i][0].isupper():
                            if oneSentArrTegget:
                                sentArr.append(' '.join(oneSentArrTegget))
                                oneSentArrTegget.clear()
                            oneSentArrTegget = self.__cleanWordWithTags__(wordArray[i], oneSentArrTegget, morph)
                        elif (re.findall('\.$|\?$|!$', wordArray[i])
                              and not re.findall('\.{3}$', wordArray[i])):
                            oneSentArrTegget = self.__cleanWordWithTags__(wordArray[i], oneSentArrTegget, morph)
                            sentArr.append(' '.join(oneSentArrTegget))
                            oneSentArrTegget.clear()
                        elif (i < len(wordArray) - 1
                              and re.findall('\.{3}$', wordArray[i])
                              and wordArray[i + 1][0].isupper()
                        ):
                            oneSentArrTegget = self.__cleanWordWithTags__(wordArray[i], oneSentArrTegget, morph)
                            sentArr.append(' '.join(oneSentArrTegget))
                            oneSentArrTegget.clear()
                        else:
                            oneSentArrTegget = self.__cleanWordWithTags__(wordArray[i], oneSentArrTegget, morph)
            else:
                if oneSentArrTegget:
                    sentArr.append(' '.join(oneSentArrTegget))
        return sentArr

    @property
    def tegedSent(self):
        return self.__makeTaggetSentArrWithPyMorphy__(self.__fileName, self.__morph)

class CorporaMaker:
    def __init__(self, pathToDirectory, outputFile, morph=None):
        self.__morph = morph
        if self.__morph is None:
            self.__morph = pymorphy2.MorphAnalyzer()
        self.__outputFile = outputFile
        self.__pathToDirectory = pathToDirectory
        self.__readFromFile__(self.__pathToDirectory)

    def __writeToCorpora__(self, outputFile, arr):
        with open(outputFile, 'a') as file:
            for it in arr:
                if it:
                    file.write(it + '\n')

    def __readFromFile__(self, wayToFile):
        files = os.listdir(wayToFile)
        for file in files:
            tempWay = os.path.join(wayToFile, file)
            if os.path.isdir(tempWay):
                print(tempWay)
                self.__readFromFile__(tempWay)
            elif file.endswith('.srt'):
                sr = SubsReader(tempWay, self.__morph)
                self.__writeToCorpora__(self.__outputFile, sr.tegedSent)
