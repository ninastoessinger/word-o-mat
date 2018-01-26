import codecs
import re


class wordChecker(object):
    """Checks lists of words against a number of specified requirements.

    Attributes:
    limitToCharset (Bool):  Signals whether output is constrained to a limited character set.
    fontChars (list):       List of characters available in current font.
    customCharset (list):   If applicable, a list of permissible characters words can use.
    requiredLetters (list): Letters required in each word (text mode).
    requiredGroups (list of lists): Groups from each of which 1 member is required (text mode).
    matchPattern (RE):      Compiled regular expression to be matched (grep mode).
    banRepetitions (Bool):  Signals whether repeating letters are banned.
    minLength (int):        Minimal word length (inclusive).
    maxLength (int):        Maximal word length (inclusive).
    matchMode (string):     Match mode to be used ("text" or "grep").

    ##### Note for future development: ideally only *either* matchPattern or required* should be required depending on the matchMode chosen; it makes no sense to pass the other stuff into this function too.
    """

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

    def _excludedAll(self, word, charList):
        """Check that no banned letter occurs in a given word.

        Can this be retired?"""
        for c in charList:
            if c in word:
                return False
        return True

    def _includedAll(self, word, charList):
        """Check that all required letters occur in a given word."""
        for c in charList:
            if not c in word:
                return False
        return True

    def _includedAny(self, word, charList):
        """Check that at least one letter in a group occurs in a given word."""
        if len(charList):
            for c in charList:
                if c in word:
                    return True
            return False
        else:
            return True

    def _includedGroups(self, word, charListList):
        """Check that all groups have at least one member present in a given word."""
        for charList in charListList:
            if not self._includedAny(word, charList):
                return False
        return True

    def _limitedTo(self, word, charList, selectedCharList, condition):
        """Check that a given word only uses the allowed scope of letters."""
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

    def _uniqueChars(self, word, condition):
        """Check that a given word does not feature repeating characters."""
        if condition:
            wordChars = []
            for c in word:
                if c in wordChars:
                    return False
                wordChars.append(c)
            return True
        else:
            return True

    def _checkLength(self, word):
        """Check that the length of a given word is within the allowed range."""
        return self.minLength <= len(word) <= self.maxLength

    def _checkExisting(self, word, outputList):
        """Check that a given word has not already been found and listed for output."""
        return not word in outputList

    def _matchRE(self, word):
        """Check that a given word matches the supplied regular expression."""
        if self.matchPatternRE is not None:
            result = self.matchPatternRE.search(word)
        if result is None:
            return False
        return True

    def checkWord(self, word, outputWords):
        """Evaluate if a given word meets all the requirements specified by the user."""

        # Compile the applicable requirements
        requirements = [
            (self._checkExisting, [outputWords]),
            (self._limitedTo, [self.fontChars, self.customCharset, self.limitToCharset]),
            (self._checkLength, []),
            (self._excludedAll, [self.bannedLetters]),
            (self._uniqueChars, [self.banRepetitions]),
        ]
        if self.matchMode == "text":
            requirements.extend([
                (self._includedAll, [self.requiredLetters]),
                (self._includedGroups, [self.requiredGroups]),
            ])
        else: # grep
            requirements.extend([
                (self._matchRE, []),
            ])

        # Run the word through all the requirements and see if it fails
        for reqFunc, args in requirements:
            if not reqFunc(word, *args):
                return False
        return True
