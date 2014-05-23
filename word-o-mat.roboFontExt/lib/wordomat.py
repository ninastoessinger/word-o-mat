# coding=utf-8
#
# Tool for RoboFont to generate test words for type testing, sketching etc.
# Default wordlist ukacd.txt is from http://www.crosswordman.com/wordlist.html
# Other languages based on Hermit Dave’s wordlists at http://invokeit.wordpress.com/frequency-word-lists/
# I assume no responsibility for inappropriate words found on those lists and rendered by this script :)
#
# v2.0 / Nina Stössinger / 30.04.2014 / KABK t]m 1314 / with thanks to Just van Rossum


import codecs
import re
from mojo.events import addObserver, removeObserver
from mojo.extensions import *
from mojo.roboFont import OpenWindow
from mojo.UI import OpenSpaceCenter, AccordionView
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
            "com.ninastoessinger.word-o-mat.limitToCharset" : "True",
            "com.ninastoessinger.word-o-mat.source" : 0
        }
        registerExtensionDefaults(initialDefaults)
        
        self.wordCount = getExtensionDefault("com.ninastoessinger.word-o-mat.wordCount")
        self.minLength = getExtensionDefault("com.ninastoessinger.word-o-mat.minLength")
        self.maxLength = getExtensionDefault("com.ninastoessinger.word-o-mat.maxLength")
        self.case = getExtensionDefault("com.ninastoessinger.word-o-mat.case")
        self.requiredLetters = []
        self.requiredGroups = [[], [], []]
        self.limitToCharset = self.readExtDefaultBoolean(getExtensionDefault("com.ninastoessinger.word-o-mat.limitToCharset")) if CurrentFont() else False
        self.banRepetitions = False
        self.randomize = True
        
        self.dictWords = {}
        self.allWords = []
        self.outputWords = []
        self.textfiles = ['ukacd', 'czech', 'danish', 'dutch', 'finnish', 'french', 'german', 'hungarian', 'italian', 'norwegian', 'slovak', 'spanish']
        self.languageNames = ['English', 'Czech', 'Danish', 'Dutch', 'Finnish', 'French', 'German', 'Hungarian', 'Italian', 'Norwegian', 'Slovak', 'Spanish']
        self.source = getExtensionDefault("com.ninastoessinger.word-o-mat.source", 0)
        
        self.loadDictionaries()
        
        # preset character groups
        groupPresets = [
            ["[lc] Ascenders", ["b", "f", "h", "k", "l"]], 
            ["[lc] Descenders", ["g", "j", "p", "q", "y"]], 
            ["[lc] Ball-and-Stick", ["b", "d", "p", "q"]], 
            ["[lc] Arches", ["n", "m", "h", "u"]], 
            ["[lc] Diagonals", ["v", "w", "x", "y"]]]
            
        addObserver(self, "fontOpened", "fontDidOpen")
        addObserver(self, "fontClosed", "fontWillClose")
        
        # dialog window
        self.w = Window((241, 259), 'word-o-mat', minSize=(241,112), maxSize=(241,459))
        interval = 25
        padd = 17
        bPadd = 3
        
        self.basicsBox = Group((padd, 8, 280, 168))
        
        self.basicsBox.wcText = TextBox((0, 3, 170, 22), 'Make this many words:') 
        self.basicsBox.wordCount = EditText((160, 0, 40, 22), text=self.wordCount, placeholder=str(20))
        
        self.basicsBox.lenTextOne = TextBox((0, 34, 60, 22), 'Length:') 
        self.basicsBox.lenTextTwo = TextBox((101, 34, 10, 22), u'–', alignment="center") 
        self.basicsBox.lenTextThree = TextBox((160, 34, 80, 22), 'letters') 
        self.basicsBox.minLength = EditText((60, 32, 39, 22), text=self.minLength, placeholder=str(3))
        self.basicsBox.maxLength = EditText((117, 32, 39, 22), text=self.maxLength, placeholder=str(10))
        
        languageOptions = list(self.languageNames)
        languageOptions.append("Local User Dictionary")
        languageOptions.append("Custom File...")
        
        self.basicsBox.source = PopUpButton((0, 68, 80, 20), [], sizeStyle="small", callback=self.changeSourceCallback) 
        self.basicsBox.source.setItems(languageOptions)
        self.basicsBox.source.set(int(self.source))
                
         
        self.basicsBox.case = PopUpButton((82, 68, 120, 20), [u"don’t change case", "all lowercase", "Capitalize", "ALL CAPS"], sizeStyle="small")
        self.basicsBox.case.set(self.case)
        
        self.basicsBox.radioGroup = RadioGroup((0, 103, 229, 46), ["Use any characters", "Limit to characters in current font", "Limit to selected glyphs"], sizeStyle="small")
        if not CurrentFont():
            self.basicsBox.radioGroup.set(0)    # Use any
            self.basicsBox.radioGroup.enable(False) # Disable selection
        else:
            if self.limitToCharset == False:
                self.basicsBox.radioGroup.set(0) # Use any
            else:
                self.basicsBox.radioGroup.set(1) # Use current font

        self.reqBox = Group((padd, 5, 270, 200))
        labelY = [8, 54]
        labelText = ["Require these letters in each word:", "Require one per group for each word:"]
        for i in range(2):
            setattr(self.reqBox, "reqLabel%s" % i, TextBox((0, labelY[i], 210, 22), labelText[i], sizeStyle="small"))
        self.reqBox.mustLettersBox = EditText((2, 24, 200, 19), text=", ".join(self.requiredLetters), sizeStyle="small")
        
        y2 = 50
        attrNameTemplate = "group%sbox"
        for i in range(3):
            j = i+1
            y2 += 22
            optionsList = ["%s: %s" % (key, ", ".join(value)) for key, value in groupPresets]
            if len(self.requiredGroups[i]) > 0 and self.requiredGroups[i][0] != "":
                optionsList.insert(0, "Recent: " + ", ".join(self.requiredGroups[i]))
            attrName = attrNameTemplate % j
            setattr(self.reqBox, attrName, ComboBox((2, y2-4, 200, 19), optionsList, sizeStyle="small")) 
        
        groupBoxes = [self.reqBox.group1box, self.reqBox.group2box, self.reqBox.group3box]
        for i in range(3):
            if len(self.requiredGroups[i]) > 0 and self.requiredGroups[i][0] != "":
                groupBoxes[i].set(", ".join(self.requiredGroups[i]))
                
        self.reqBox.checkbox0 = CheckBox((bPadd, 140, 18, 18), "", sizeStyle="small", value=self.banRepetitions)
        self.reqBox.checkLabel = TextBox((18, 145, -bPadd, 18), "No repeating characters in words", sizeStyle="small")
          
        self.optionsBox = Group((padd, 5, 270, interval*1.5))
        self.optionsBox.submit = Button((0, 1, 201, 22), 'words please!', callback=self.makeWords)
        
        accItems = [
                       dict(label="Main controls", view=self.basicsBox, size=169, collapsed=False, canResize=False),
                       dict(label="Require specific letters", view=self.reqBox, size=177, collapsed=True, canResize=False),
                       dict(label="Go for it", view=self.optionsBox, size=37, collapsed=False, canResize=False)
                       ]     
        self.w.accView = AccordionView((0, 0, 290, -0), accItems)
        
        self.w.bind("close", self.windowClose)
        self.w.setDefaultButton(self.optionsBox.submit)
        self.w.open()
        
    def readExtDefaultBoolean(self, string): 
        if string == "True": 
            return True
        return False
        
    def writeExtDefaultBoolean(self, var): 
        if var == True: 
            return "True"
        return "False"
        
    def loadDictionaries(self):
        bundle = ExtensionBundle("word-o-mat")
        contentLimit  = '*****' # If word list file contains a header (e.g. copyright notice), script will start looking for content after this delimiter
        
        # read included textfiles
        for textfile in self.textfiles:
            path = bundle.getResourceFilePath(textfile)
            fo = codecs.open(path, mode="r", encoding="utf-8")
            lines = fo.read()
            fo.close()
                
            self.dictWords[textfile] = lines.splitlines()
            try:
                contentStart = self.dictWords[textfile].index(contentLimit) + 1
                self.dictWords[textfile] = self.dictWords[textfile][contentStart:]
            except ValueError:
                pass
            #print "word-o-mat: wordlist %s loaded" % textfile
            
        # read user dictionary
        userFile = open('/usr/share/dict/words', 'r')
        lines = userFile.read()
        self.dictWords["user"] = lines.splitlines()
        
        
    def changeSourceCallback(self, sender):
        customIndex = len(self.textfiles) + 1
        if sender.get() == customIndex: # Custom word list
            try:
                filePath = getFile(title="Load custom word list", messageText="Select a text file with words on separate lines", fileTypes=["txt"])[0]
            except TypeError:
                filePath = None
                self.customWords = []
                print "word-o-mat: Input of custom word list canceled, using default"
            if filePath is not None:
                fo = codecs.open(filePath, mode="r", encoding="utf-8")
                lines = fo.read()
                fo.close()
                
                self.customWords = lines.splitlines()
                # It seems these are correct internally. 
                # For output we might have to convert to other encodings, for instance:
                # Message(self.customWords[3].encode('iso-8859-1'))
                    
    def fontCharacters(self, font):
        if not font:
            return []
        charset = []    
        for g in font:
            # charset.append(g.name)
            if g.unicode is not None:
                try:
                    charset.append(unichr(int(g.unicode)))
                except ValueError:
                    pass
        return charset
        
    def getInputString(self, field, stripColon):
        inputString = field.get()
        pattern = re.compile(" *, *| +")
        if stripColon:
            i = inputString.find(":")
            if i != -1:
                inputString = inputString[i+1:]
        result = pattern.split(inputString)
        result = [unicode(s) for s in result if s]
        return result
        
    def getIntegerValue(self, field):
        try:
            returnValue = int(field.get())
        except ValueError:
            returnValue = int(field.getPlaceholder())
            field.set(returnValue)
        return returnValue
        
    def checkReqVsFont(self, required, limitTo, fontChars, customCharset):
        if limitTo == False:
            return True
        else:
            if len(customCharset) > 0:
                useCharset = customCharset
                messageCharset = "selection of glyphs you would like me to use"
            else:
                useCharset = fontChars
                messageCharset = "font"
            for c in required:
                if not c in useCharset:
                    Message ("Conflict: Character \"%s\" was specified as required, but not found in the %s." % (c, messageCharset))
                    return False
            return True
        
    def checkReqVsLen(self, required, maxLength):
        if len(required) > maxLength:
            Message ("Conflict: Required characters exceed maximum word length. Please revise.")
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
        
    def checkInput(self, limitTo, fontChars, customCharset, required, minLength, maxLength, case):
        requirements = [  
            (self.checkReqVsLen, [required, maxLength]),
            (self.checkReqVsFont, [required, limitTo, fontChars, customCharset]),
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
        self.wordCount = self.getIntegerValue(self.basicsBox.wordCount)
        self.minLength = self.getIntegerValue(self.basicsBox.minLength)
        self.maxLength = self.getIntegerValue(self.basicsBox.maxLength)
        self.case = self.basicsBox.case.get()
        self.customCharset = []
        
        charset = self.basicsBox.radioGroup.get()
        self.limitToCharset = True
        if charset == 0:
            self.limitToCharset = False
        else:
            if charset == 2: # use selection
                if len(self.f.selection) == 0: #nothing selected
                    Message("No glyphs were selected in the font window. Word-o-mat will use any characters available in the font.")
                    self.basicsBox.radioGroup.set(1) # use font chars
                else:
                    try:
                        #self.customCharset = self.f.selection # this just gives me the font names
                        self.customCharset = []
                        for gname in self.f.selection:
                            if self.f[gname].unicode is not None: # make sure this does what it should
                                try: 
                                    self.customCharset.append(unichr(int(self.f[gname].unicode)))
                                except ValueError:
                                    pass 
                        for entry in self.customCharset:
                            print entry
                    except AttributeError: 
                        pass        
                
        self.requiredLetters = self.getInputString(self.reqBox.mustLettersBox, False)
        self.requiredGroups[0] = self.getInputString(self.reqBox.group1box, True) 
        self.requiredGroups[1] = self.getInputString(self.reqBox.group2box, True) 
        self.requiredGroups[2] = self.getInputString(self.reqBox.group3box, True)
        self.banRepetitions = self.reqBox.checkbox0.get()
        self.outputWords = [] #initialize/empty
        
        
        self.source = self.basicsBox.source.get()
        languageCount = len(self.textfiles)
        if self.source == languageCount: # User Dictionary    
            self.allWords = self.dictWords["user"]
        elif self.source == languageCount+1: # Custom word list
            try:
                if self.customWords != []:
                    self.allWords = self.customWords
                else:
                    self.allWords = self.dictWords["ukacd"] 
                    self.basicsBox.source.set(0)
            except AttributeError:
                self.allWords = self.dictWords["ukacd"] 
                self.basicsBox.source.set(0)
        else: # language lists
            for i in range(languageCount):
                if self.source == i:
                    self.allWords = self.dictWords[self.textfiles[i]]
                
        # store new values as defaults
        extDefaults = {
            "wordCount": self.wordCount, 
            "minLength": self.minLength, 
            "maxLength": self.maxLength, 
            "case": self.case, 
            "limitToCharset": self.writeExtDefaultBoolean(self.limitToCharset), 
            "source": self.source,
            }
        for key, value in extDefaults.iteritems():
            setExtensionDefault("com.ninastoessinger.word-o-mat."+key, value)
                
        # go make words
        if self.checkInput(self.limitToCharset, self.fontChars, self.customCharset, self.requiredLetters, self.minLength, self.maxLength, self.case) == True:
        
            checker = wordChecker(self.limitToCharset, self.fontChars, self.customCharset, self.requiredLetters, self.requiredGroups, self.banRepetitions, self.minLength, self.maxLength)
            for i in self.allWords:
                if len(self.outputWords) >= self.wordCount:
                    break
                else:
                    w = choice(self.allWords)
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
        self.basicsBox.radioGroup.enable(True)
         
    def fontClosed(self, info):
        if len(AllFonts()) <= 1:
            self.basicsBox.radioGroup.set(0) # use any 
            self.basicsBox.radioGroup.enable(False) 
         
    def windowClose(self, sender):
        removeObserver(self, "fontDidOpen")
        removeObserver(self, "fontWillClose")

OpenWindow(WordomatWindow)