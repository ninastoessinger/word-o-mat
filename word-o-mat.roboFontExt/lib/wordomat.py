# Tool for Robofont to generate test words for type testing, sketching etc.
# Default wordlist ukacd.txt is from http://www.crosswordman.com/wordlist.html
# v1.0 / Nina Stössinger 29.11.2013 / with thanks to Just van Rossum / KABK t]m 1314

from vanilla import * 
from mojo.UI import CurrentSpaceCenter
from mojo.extensions import ExtensionBundle
from robofab.interface.all.dialogs import Message
from random import choice
import re
from wordcheck import wordChecker

f = CurrentFont()
warned = False

class WordomatWindow:
    def __init__(self):
        # set defaults
        self.wordCount = 20
        self.minLength = 3
        self.maxLength = 10
        self.requiredLetters = ['a', 'o']
        self.bannedLetters = ['-']
        self.requiredGroups = [[], [], []]
        self.limitToCharset = False
        self.banRepetitions = False
        self.randomize = True
        self.outputWords = []
        
        fileName      = 'ukacd'
        contentLimit  = '*****' # If word list file contains a header (e.g. copyright notice), start looking for content after this delimiter
        
        bundle = ExtensionBundle("word-o-mat")
        fo = open(bundle.getResourceFilePath(fileName, ext="txt"))
        lines = fo.read()
        fo.close()
        self.allWords = lines.splitlines()
        try:
            contentStart = self.allWords.index(contentLimit) + 1
            self.allWords = self.allWords[contentStart:]
        except ValueError:
            pass
        
        # preset character groups
        groupPresets = [
            ["Ascenders", ["b", "f", "h", "k", "l"]], 
            ["Descenders", ["g", "j", "p", "q", "y"]], 
            ["Ball-and-Stick", ["b", "d", "p", "q"]], 
            ["Arches", ["n", "m", "h", "u"]], 
            ["Diagonals", ["v", "w", "x", "y"]]]
        
        # dialog window
        self.w = FloatingWindow((325, 488), 'word-o-mat')
        interval = 28
        padding = 10
        boxPadding = 3
        y = 10
        
        self.w.basicsBox = Box((padding, y, -padding, interval*2.75))
        self.w.basicsBox.wcText = TextBox((boxPadding, 5, 170, 22), 'Make this many words:') 
        self.w.basicsBox.lenTextOne = TextBox((boxPadding, 5 + interval * 1.25, 90, 22), 'Word length:') 
        self.w.basicsBox.lenTextTwo = TextBox((141, 5 + interval * 1.25, 20, 22), 'to') 
        self.w.basicsBox.lenTextThree = TextBox((212, 5 + interval * 1.25, 80, 22), 'characters') 
        self.w.basicsBox.wordCount = EditText((160, 3, 40, 22), text=self.wordCount, placeholder=str(20))
        self.w.basicsBox.minLength = EditText((95, 3 + interval * 1.25, 40, 22), text=self.minLength, placeholder=str(3))
        self.w.basicsBox.maxLength = EditText((165, 3 + interval * 1.25, 40, 22), text=self.maxLength, placeholder=str(10))     
        y += interval*3.125

        self.w.reqBox = Box((padding, y, -padding, interval*8.9))
        labelY = [5, 5 + interval*2.25, 5 + interval*6.375]
        labelText = ["Required characters:", "Groups (require at least one in each group):", "Excluded characters:"]
        for i in range(3):
            setattr(self.w.reqBox, "reqLabel%s" % i, TextBox((boxPadding, labelY[i], -boxPadding, 22), labelText[i]))
        self.w.reqBox.mustLettersBox = EditText((boxPadding, 5 + interval*.8, -boxPadding, 22), text=", ".join(self.requiredLetters))
        self.w.reqBox.notLettersBox = EditText((boxPadding, 5 + interval * 7.175, -boxPadding, 22), text=", ".join(self.bannedLetters))
        
        y2 = interval*2.25
        attrNameTemplate = "group%sbox"
        for i in range(3):
            j = i+1
            y2 += interval
            optionsList = ["%s: %s" % (key, ", ".join(value)) for key, value in groupPresets]
            if len(self.requiredGroups[i]) > 0:
                optionsList.insert(0, "Current: " + ", ".join(self.requiredGroups[i]))
            attrName = attrNameTemplate % j
            setattr(self.w.reqBox, attrName, ComboBox((boxPadding, y2-3, -boxPadding, 22), optionsList)) 
        y += interval*9.25
          
        self.w.optionsBox = Box((padding, y, -padding, interval*3.125))
        chkNameTemplate = "checkbox%s"
        chkLabel = ["Limit to characters available in current font", "No repeating characters", "Randomize output"]
        chkValues = [self.limitToCharset, self.banRepetitions, self.randomize]
        for i in range(3):
            y3 = i*interval*.875
            attrName = chkNameTemplate % i
            setattr(self.w.optionsBox, attrName, CheckBox((boxPadding, y3+3, -boxPadding, 22), chkLabel[i], value=chkValues[i])) 
        self.w.optionsBox.checkbox0.enable(f)   
        y += interval*3.5
        self.w.submit = Button((10,y,-10, 22), 'words please!', callback=self.makeWords)
        self.w.open()
    
    def fontCharacters(self):
        global warned
        if not f:
            if warned == False:
                Message("No open fonts found; word-o-mat will output to the Output Window.")
                warned = True
            return []
        charset = []
        for g in f:
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
        try:
            result = [str(s) for s in result if s]
        except UnicodeEncodeError:
            print "Sorry! Characters beyond a-z/A-Z are not currently supported. Please adjust your input."
            result = []
        return result
        
    def getIntegerValue(self, field):
        try:
            returnValue = int(field.get())
        except ValueError:
            returnValue = int(field.getPlaceholder())
            field.set(returnValue)
        return returnValue
                
    def makeWords(self, sender=None):
        global warned
        self.wordCount = self.getIntegerValue(self.w.basicsBox.wordCount)
        self.minLength = self.getIntegerValue(self.w.basicsBox.minLength)
        self.maxLength = self.getIntegerValue(self.w.basicsBox.maxLength)
        self.requiredLetters = self.getInputString(self.w.reqBox.mustLettersBox, False) 
        self.requiredGroups[0] = self.getInputString(self.w.reqBox.group1box, True) 
        self.requiredGroups[1] = self.getInputString(self.w.reqBox.group2box, True) 
        self.requiredGroups[2] = self.getInputString(self.w.reqBox.group3box, True) 
        self.bannedLetters = self.getInputString(self.w.reqBox.notLettersBox, False)
        self.bannedLetters.append(" ")
        self.limitToCharset = self.w.optionsBox.checkbox0.get()
        self.banRepetitions = self.w.optionsBox.checkbox1.get()
        self.randomize = self.w.optionsBox.checkbox2.get()
        self.fontChars = self.fontCharacters()
        self.outputWords = [] #initialize/empty
        
        checker = wordChecker(self.limitToCharset, self.fontChars, self.requiredLetters, self.requiredGroups, self.bannedLetters, self.banRepetitions, self.minLength, self.maxLength)
        for i in self.allWords:
            if len(self.outputWords) >= self.wordCount:
                break
            else:
                if self.randomize:
                    w = choice(self.allWords)
                else:
                    w = i
                if checker.checkWord(w, self.outputWords):
                    self.outputWords.append(w)  
        # output
        if len(self.outputWords) < 1:
            print "word-o-mat: No matching words found <sad trombone>"
        else:
            outputString = " ".join(self.outputWords)
            c = CurrentSpaceCenter()
            try:
                c.setRaw(outputString)
            except:
                if f:
                    if warned == False:
                        Message("No open Space Center found; word-o-mat will output to the Output Window.")
                        warned = True
                print "word-o-mat:", outputString
                pass
    
w = WordomatWindow()