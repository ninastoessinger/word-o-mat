# Tool for Robofont to generate test words for type testing, sketching etc.
# Default wordlist ukacd.txt is from http://www.crosswordman.com/wordlist.html
# I assume no responsibility for inappropriate words found on that list and rendered by this script!
# v1.2 / Nina Stössinger 10.12.2013 / with thanks to Just van Rossum / KABK t]m 1314

import codecs
import re
from mojo.events import addObserver, removeObserver
from mojo.extensions import ExtensionBundle, getExtensionDefault, setExtensionDefault, registerExtensionDefaults
from mojo.roboFont import OpenWindow
from mojo.UI import OpenSpaceCenter
from random import choice
from robofab.interface.all.dialogs import Message
from vanilla import * 
from vanilla.dialogs import getFile
from wordcheck import wordChecker 

warned = False

class WordomatWindow:
    def __init__(self):
        initialDefaults = {
            "com.ninastoessinger.word-o-mat.wordCount" : 20,
            "com.ninastoessinger.word-o-mat.minLength" : 3,
            "com.ninastoessinger.word-o-mat.maxLength" : 15,
            "com.ninastoessinger.word-o-mat.case" : 0,
            "com.ninastoessinger.word-o-mat.requiredLetters" : "",
            "com.ninastoessinger.word-o-mat.bannedLetters" : "",
            "com.ninastoessinger.word-o-mat.requiredGroup0" : "",
            "com.ninastoessinger.word-o-mat.requiredGroup1" : "",
            "com.ninastoessinger.word-o-mat.requiredGroup2" : "",
            "com.ninastoessinger.word-o-mat.limitToCharset" : "True",
            "com.ninastoessinger.word-o-mat.banRepetitions" : "False",
            "com.ninastoessinger.word-o-mat.randomize" : "True",
        }
        registerExtensionDefaults(initialDefaults)
        
        self.wordCount = getExtensionDefault("com.ninastoessinger.word-o-mat.wordCount")
        self.minLength = getExtensionDefault("com.ninastoessinger.word-o-mat.minLength")
        self.maxLength = getExtensionDefault("com.ninastoessinger.word-o-mat.maxLength")
        self.case = getExtensionDefault("com.ninastoessinger.word-o-mat.case")
        self.requiredLetters = getExtensionDefault("com.ninastoessinger.word-o-mat.requiredLetters")
        self.bannedLetters = getExtensionDefault("com.ninastoessinger.word-o-mat.bannedLetters")
        self.requiredGroups = [[], [], []]
        for i in range(len(self.requiredGroups)):
            self.requiredGroups[i] = getExtensionDefault("com.ninastoessinger.word-o-mat.requiredGroup"+str(i))
        self.limitToCharset = self.readExtDefaultBoolean(getExtensionDefault("com.ninastoessinger.word-o-mat.limitToCharset")) if CurrentFont() else False
        self.banRepetitions = self.readExtDefaultBoolean(getExtensionDefault("com.ninastoessinger.word-o-mat.banRepetitions"))
        self.randomize = self.readExtDefaultBoolean(getExtensionDefault("com.ninastoessinger.word-o-mat.randomize"))
        
        self.allWords = []
        self.outputWords = []
        
        # read included textfile
        fileName      = 'ukacd'
        contentLimit  = '*****' # If word list file contains a header (e.g. copyright notice), start looking for content after this delimiter
        bundle = ExtensionBundle("word-o-mat")
        fo = open(bundle.getResourceFilePath(fileName, ext="txt"))
        lines = fo.read()
        fo.close()
        self.ukacdWords = lines.splitlines()
        try:
            contentStart = self.ukacdWords.index(contentLimit) + 1
            self.ukacdWords = self.ukacdWords[contentStart:]
        except ValueError:
            pass
            
        # read user dictionary
        userFile = open('/usr/share/dict/words', 'r')
        lines = userFile.read()
        self.userWords = lines.splitlines()
        
        # preset character groups
        groupPresets = [
            ["Ascenders", ["b", "f", "h", "k", "l"]], 
            ["Descenders", ["g", "j", "p", "q", "y"]], 
            ["Ball-and-Stick", ["b", "d", "p", "q"]], 
            ["Arches", ["n", "m", "h", "u"]], 
            ["Diagonals", ["v", "w", "x", "y"]]]
            
        addObserver(self, "fontOpened", "fontDidOpen")
        addObserver(self, "fontClosed", "fontWillClose")
        
        # dialog window
        self.w = FloatingWindow((325, 482), 'word-o-mat')
        interval = 25
        padd = 10
        bPadd = 3
        y = 10
        
        self.w.basicsBox = Box((padd, y, -padd, interval*4.85))
        self.w.basicsBox.wcText = TextBox((bPadd, 5, 170, 22), 'Make this many words:') 
        self.w.basicsBox.lenTextOne = TextBox((bPadd, 5 + interval * 1.25, 90, 22), 'Word length:') 
        self.w.basicsBox.lenTextTwo = TextBox((141, 5 + interval * 1.25, 20, 22), 'to') 
        self.w.basicsBox.lenTextThree = TextBox((212, 5 + interval * 1.25, 80, 22), 'characters') 
        self.w.basicsBox.wordCount = EditText((160, 3, 40, 22), text=self.wordCount, placeholder=str(20))
        self.w.basicsBox.minLength = EditText((95, 3 + interval * 1.25, 40, 22), text=self.minLength, placeholder=str(3))
        self.w.basicsBox.maxLength = EditText((165, 3 + interval * 1.25, 40, 22), text=self.maxLength, placeholder=str(10))  
        self.w.basicsBox.caseLabel = TextBox((bPadd, 3 + interval * 2.55, 60, 22), 'Case:') 
        self.w.basicsBox.case = PopUpButton((65, 2 + interval * 2.55, -10, 20), ["leave as is", "all lowercase", "Capitalize", "ALL CAPS"])
        self.w.basicsBox.case.set(self.case)
        self.w.basicsBox.sourceLabel = TextBox((bPadd, 6 + interval * 3.55, 60, 22), 'Source:', sizeStyle="mini") 
        self.w.basicsBox.source = PopUpButton((65, 2 + interval * 3.55, -10, 20), ["Included word list (bigger)", "User Dictionary (faster)", "Custom..."], sizeStyle="mini", callback=self.changeSourceCallback)
        y += interval*5.2

        self.w.reqBox = Box((padd, y, -padd, interval*8.625))
        labelY = [5, 7 + interval*2, 6 + interval*6]
        labelText = ["Obligatory characters:", "Groups:", "Banned characters:", "(must be in each word)", "(require one per group for each word)", "(must not occur)"]
        for i in range(3):
            setattr(self.w.reqBox, "reqLabel%s" % i, TextBox((bPadd, labelY[i], -bPadd, 22), labelText[i]))
        for i in range(3,6):
            setattr(self.w.reqBox, "reqLabel%s" % i, TextBox((bPadd+50, labelY[i-3]+5, -bPadd, 22), labelText[i], sizeStyle="mini", alignment="right"))   
        self.w.reqBox.mustLettersBox = EditText((bPadd+2, 2 + interval, -bPadd, 19), text=", ".join(self.requiredLetters), sizeStyle="small")
        self.w.reqBox.notLettersBox = EditText((bPadd+2, 3 + interval * 7, -bPadd, 19), text=", ".join(self.bannedLetters), sizeStyle="small")
        
        y2 = interval*2.25
        attrNameTemplate = "group%sbox"
        for i in range(3):
            j = i+1
            y2 += interval
            optionsList = ["%s: %s" % (key, ", ".join(value)) for key, value in groupPresets]
            if len(self.requiredGroups[i]) > 0 and self.requiredGroups[i][0] != "":
                optionsList.insert(0, "Recent: " + ", ".join(self.requiredGroups[i]))
            attrName = attrNameTemplate % j
            setattr(self.w.reqBox, attrName, ComboBox((bPadd+2, y2-4, -bPadd, 19), optionsList, sizeStyle="small")) 
        y += interval*9
        
        groupBoxes = [self.w.reqBox.group1box, self.w.reqBox.group2box, self.w.reqBox.group3box]
        for i in range(3):
            if len(self.requiredGroups[i]) > 0 and self.requiredGroups[i][0] != "":
                groupBoxes[i].set(", ".join(self.requiredGroups[i]))
          
        self.w.optionsBox = Box((padd, y, -padd, interval*3.125))
        chkNameTemplate = "checkbox%s"
        chkLabel = ["Limit to characters available in current font", "No repeating characters", "Randomize output"]
        chkValues = [self.limitToCharset, self.banRepetitions, self.randomize]
        for i in range(3):
            y3 = i*interval*.875
            attrName = chkNameTemplate % i
            setattr(self.w.optionsBox, attrName, CheckBox((bPadd, y3+3, -bPadd, 22), chkLabel[i], value=chkValues[i])) 
        self.w.optionsBox.checkbox0.enable(CurrentFont())
        y += interval*3.45
        self.w.submit = Button((10,y,-10, 22), 'words please!', callback=self.makeWords)
        self.w.bind("close", self.windowClose)
        self.w.open()
        
    def readExtDefaultBoolean(self, string): 
        if string == "True": 
            return True
        return False
        
    def writeExtDefaultBoolean(self, var): 
        if var == True: 
            return "True"
        return "False"
        
    def changeSourceCallback(self, sender):
        if sender.get() == 2: # Custom word list - this is very much in beta
            try:
                filePath = getFile(title="Load custom word list", messageText="Select a text file with words on separate lines", fileTypes=["txt"])[0]
            except TypeError:
                filePath = None
                self.customWords = []
                print "word-o-mat: Input of custom word list canceled, using default"
            if filePath is not None:
                try:
                    fo = codecs.open(filePath, mode="r", encoding="utf-8")
                    lines = fo.read()
                except UnicodeDecodeError:
                    fo = open(filePath, 'r')
                    lines = fo.read()
                fo.close()
                self.customWords = [line.decode('utf-8') for line in lines.splitlines()] # this throws errors, why?
                # this below variation silences the errors but skips words with special characters
                # maybe I need to explicitly work with unicodes instead of strings 
                # but not now
                #try:
                #    self.customWords = [line.decode('utf-8') for line in lines.splitlines()] # this throws errors      
                #except:          
                #    self.customWords = lines.splitlines()
                ### END UNICODE BAUSTELLE
                    
    def fontCharacters(self, font):
        if not font:
            return []
        charset = []
        for g in font:
            charset.append(g.name)
        return charset
        
    def getInputString(self, field, stripColon):
        inputString = field.get()
        pattern = re.compile(" *, *| +")
        if stripColon:
            i = inputString.find(":")
            if i != -1:
                inputString = inputString[i+1:]
        result = pattern.split(inputString)
        #result = [str(s) for s in result if s]
        result = [unicode(s) for s in result if s]
        #try:
        #    result = [str(s) for s in result if s]
        #except UnicodeEncodeError:
        #    Message ("Sorry! Characters beyond a-z/A-Z are not currently supported. Please adjust your input.")
        #    result = []
        return result
        
    def getIntegerValue(self, field):
        try:
            returnValue = int(field.get())
        except ValueError:
            returnValue = int(field.getPlaceholder())
            field.set(returnValue)
        return returnValue
        
    def checkReqBanned(self, required, banned):
        for b in banned:
            if b in required:
                Message ("Conflict: Character \"%s\" is both required and banned. Please fix." % b)
                return False
        return True
        
    def checkReqVsFont(self, required, limitTo, fontChars):
        if limitTo == False:
            return True
        else:
            for c in required:
                if not c in fontChars:
                    Message ("Conflict: Character \"%s\" was specified as obligatory, but not found in the font." % c)
                    return False
            return True
        
    def checkReqVsLen(self, required, maxLength):
        if len(required) > maxLength:
            Message ("Conflict: Obligatory characters exceed maximum word length. Please revise.")
            return False
        return True
        
    def checkReqVsCase(self, required, case):
        #if case == 1: # all lowercase
        #    lc = re.compile("[a-z]")
        #    for c in required:
        #        m = lc.match(c)
        #        if not m:
        #            Message ("Conflict: You appear to want all-lowercase words, but have specified non-lowercase characters as required. Please revise.")
        #            return False
        #    return True
        #elif case == 3: # all caps
        #    uc = re.compile("[A-Z]")
        #    for c in required:
        #        m = uc.match(c)
        #        if not m:
        #            Message ("Conflict: You appear to want words in all-caps, but have specified lowercase characters as required. Please revise.")
        #            return False
        #    return True
        #else:
            return True
        
    def checkMinVsMax(self, minLength, maxLength):
        if not minLength <= maxLength:
            Message ("Confusing input for minimal/maximal word length. Please fix.")
            return False
        return True
        
    def checkInput(self, limitTo, fontChars, required, banned, minLength, maxLength, case):
        requirements = [
            (self.checkReqBanned, [required, banned]),    
            (self.checkReqVsLen, [required, maxLength]),
            (self.checkReqVsFont, [required, limitTo, fontChars]),
            (self.checkReqVsCase, [required, case]),
            (self.checkMinVsMax, [minLength, maxLength]),
        ]
        for reqFunc, args in requirements:
            if not reqFunc(*args):
                return False
        return True
                
    def makeWords(self, sender=None):
        global warned
        self.f = CurrentFont()
        self.fontChars = self.fontCharacters(self.f)
        self.wordCount = self.getIntegerValue(self.w.basicsBox.wordCount)
        self.minLength = self.getIntegerValue(self.w.basicsBox.minLength)
        self.maxLength = self.getIntegerValue(self.w.basicsBox.maxLength)
        self.case = self.w.basicsBox.case.get()
        self.requiredLetters = self.getInputString(self.w.reqBox.mustLettersBox, False) 
        self.requiredGroups[0] = self.getInputString(self.w.reqBox.group1box, True) 
        self.requiredGroups[1] = self.getInputString(self.w.reqBox.group2box, True) 
        self.requiredGroups[2] = self.getInputString(self.w.reqBox.group3box, True) 
        self.bannedLetters = self.getInputString(self.w.reqBox.notLettersBox, False)
        self.limitToCharset = self.w.optionsBox.checkbox0.get()
        self.banRepetitions = self.w.optionsBox.checkbox1.get()
        self.randomize = self.w.optionsBox.checkbox2.get()
        self.outputWords = [] #initialize/empty
        
        self.source = self.w.basicsBox.source.get()
        if self.source == 0:
            self.allWords = self.ukacdWords 
        elif self.source == 1:
            self.allWords = self.userWords
        elif self.source == 2:
            if self.customWords and self.customWords != []:
                self.allWords = self.customWords
            else:
                self.allWords = self.ukacdWords 
                self.w.basicsBox.source.set(0)
                
        # store new values as defaults
        extDefaults = {
            "wordCount": self.wordCount, 
            "minLength": self.minLength, 
            "maxLength": self.maxLength, 
            "case": self.case, 
            "requiredLetters": self.requiredLetters,
            "requiredGroup0": self.requiredGroups[0],
            "requiredGroup1": self.requiredGroups[1],
            "requiredGroup2": self.requiredGroups[2],
            "bannedLetters": self.bannedLetters,
            "limitToCharset": self.writeExtDefaultBoolean(self.limitToCharset), 
            "banRepetitions": self.writeExtDefaultBoolean(self.banRepetitions), 
            "randomize": self.writeExtDefaultBoolean(self.randomize),
            }
        for key, value in extDefaults.iteritems():
            setExtensionDefault("com.ninastoessinger.word-o-mat."+key, value)
                
        # go make words
        if self.checkInput(self.limitToCharset, self.fontChars, self.requiredLetters, self.bannedLetters, self.minLength, self.maxLength, self.case) == True:
        
            checker = wordChecker(self.limitToCharset, self.fontChars, self.requiredLetters, self.requiredGroups, self.bannedLetters, self.banRepetitions, self.minLength, self.maxLength)
            for i in self.allWords:
                if len(self.outputWords) >= self.wordCount:
                    break
                else:
                    if self.randomize:
                        w = choice(self.allWords)
                    else:
                        w = i
                    if self.case == 1:   w = w.lower()
                    elif self.case == 2: w = w.title()
                    elif self.case == 3: w = w.upper()
                    if checker.checkWord(w, self.outputWords):
                        self.outputWords.append(w)  
            # output
            if len(self.outputWords) < 1:
                Message("word-o-mat: no matching words found <sad trombone>")
            else:
                outputString = " ".join(self.outputWords)
                try:
                    sp = OpenSpaceCenter(CurrentFont())
                    sp.setRaw(outputString)
                except:
                    if warned == False:
                        Message("No open fonts found; word-o-mat will output to the Output Window.")
                    warned = True
                    print "word-o-mat:", outputString
        else:
            print "word-o-mat: Aborted because of errors"
    
    def fontOpened(self, info):
        self.w.optionsBox.checkbox0.enable(True)
        self.w.optionsBox.checkbox0.set(True)
         
    def fontClosed(self, info):
        if len(AllFonts()) <= 1:
            self.w.optionsBox.checkbox0.set(False) 
            self.w.optionsBox.checkbox0.enable(False) 
         
    def windowClose(self, sender):
        removeObserver(self, "fontDidOpen")
        removeObserver(self, "fontWillClose")

OpenWindow(WordomatWindow)