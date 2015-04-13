import codecs
import re
from robofab.interface.all.dialogs import Message

class wordChecker(object):
    def __init__(self, limitToCharset, fontChars, customCharset, requiredLetters, requiredGroups, matchPattern, banRepetitions, minLength, maxLength, matchMode="text"):
        self.limitToCharset = limitToCharset
        self.fontChars = fontChars
        self.customCharset = customCharset
        self.bannedLetters = [" "] # spaces are banned inside words

        self.matchMode = matchMode
        if self.matchMode == "text":
            self.requiredLetters = requiredLetters
            self.requiredGroups = requiredGroups
        else: #grep
            self.matchPatternRE = matchPattern
        self.banRepetitions = banRepetitions
        self.minLength = minLength
        self.maxLength = maxLength

    def excludedAll(self, word, charList):
        for c in charList:
            if c in word:
                return False
        return True

    def includedAll(self, word, charList):
        #word = unicode(word)
        for c in charList:
            if not c in word: # this throws a UnicodeDecodeError when c is non-ASCII
                return False
        return True

    def includedAny(self, word, charList):
        if len(charList):
            for c in charList:
                if c in word:
                    return True
            return False
        else:
            return True

    def includedGroups(self, word, charListList):
        for charList in charListList:
            if not self.includedAny(word, charList):
                return False
        return True

    def limitedTo(self, word, charList, selectedCharList, condition):
        if len(selectedCharList) > 0:
            useList = selectedCharList
        else:
            useList = charList
        if condition:
            for c in word:
                if not c in useList:
                    return False
            return True
        else:
            return True

    def uniqueChars(self, word, condition):
        if condition:
            wordChars = []
            for c in word:
                if c in wordChars:
                    return False
                wordChars.append(c)
            return True
        else:
            return True

    def checkLength(self, word):
        return self.minLength <= len(word) <= self.maxLength

    def checkExisting(self, word, outputList):
        return not word in outputList

    def matchRE(self, word):
    	if self.matchPatternRE is not None:
	    	result = self.matchPatternRE.search(word)
	    	if result is None:
	    		return False
    	return True

    def checkWord(self, word, outputWords):
    	requirements = [
	           (self.checkExisting, [outputWords]),    
	           (self.limitedTo, [self.fontChars, self.customCharset, self.limitToCharset]),
	           (self.checkLength, []),
	           (self.excludedAll, [self.bannedLetters]),
	           (self.uniqueChars, [self.banRepetitions]),
	       ]
        if self.matchMode == "text":
	       requirements.extend([
	           (self.includedAll, [self.requiredLetters]),
	           (self.includedGroups, [self.requiredGroups]),
	       ])
        else: # grep
            requirements.extend([
	           (self.matchRE, []),
	       ])
        #print requirements
        for reqFunc, args in requirements:
            if not reqFunc(word, *args):
                return False
        return True
