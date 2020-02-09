# coding=utf-8
#
"""
word-o-mat is a RoboFont extension that generates test words for type testing, sketching etc.
I assume no responsibility for inappropriate words found on those lists and rendered by this script :)

v2.2.4 / Nina Stössinger / 31.05.2015
Thanks to Just van Rossum, Frederik Berlaen, Tobias Frere-Jones, Joancarles Casasín, James Edmondson
Also to Roberto Arista, Sindre Bremnes, Mathieu Christe/David Hodgetts for help with wordlists
"""

import codecs
import re
import webbrowser

from lib.UI.noneTypeColorWell import NoneTypeColorWell
from lib.UI.spaceCenter.glyphSequenceEditText import GlyphSequenceEditText

from mojo.events import addObserver, removeObserver
from mojo.extensions import *
from mojo.roboFont import OpenWindow
from mojo.UI import OpenSpaceCenter, AccordionView

from vanilla.dialogs import getFile, message
from vanilla import *

from random import choice

import wordcheck

try:
    reload
except NameError:
    # in py3
    from importlib import reload

reload(wordcheck)



warned = False


class WordomatWindow:

    def __init__(self):
        """Initialize word-o-mat UI, open the window."""

        # load stuff
        self.loadPrefs()
        self.loadDictionaries()

        # Observers for font events
        addObserver(self, lambda: self.g1.base.enable(True), "fontDidOpen")
        addObserver(self, "fontClosed", "fontWillClose")

        # The rest of this method is just building the window / interface

        self.w = Window((250, 414), 'word-o-mat', minSize=(250,111), maxSize=(250,436))
        padd, bPadd = 12, 3
        groupW = 250 - 2*padd

        # Panel 1 - Basic Settings
        self.g1 = Group((padd, 8, groupW, 104))

        topLineFields = {
            "wordCount": [0,   self.wordCount, 20],
            "minLength": [108, self.minLength, 3],
            "maxLength": [145, self.maxLength, 10],
        }
        topLineLabels = {
            "wcText": [31, 78, 'words with', 'left'],
            "lenTextTwo": [133, 10, u'–', 'center'],
            "lenTextThree": [176, -0, 'letters', 'left'],
        }

        for label, values in topLineFields.items():
            setattr(self.g1, label, EditText((values[0], 0, 28, 22), text=values[1], placeholder=str(values[2])))

        for label, values in topLineLabels.items():
            setattr(self.g1, label, TextBox((values[0], 3, values[1], 22), text=values[2], alignment=values[3]))


        # language selection
        languageOptions = list(self.languageNames)
        languageOptions.extend(["OSX Dictionary", "Any language", "Custom wordlist..."])
        self.g1.source = PopUpButton((0, 32, 85, 20), [], sizeStyle="small", callback=self.changeSourceCallback)
        self.g1.source.setItems(languageOptions)
        self.g1.source.set(int(self.source))

        # case selection
        caseList = [u"don’t change case", "make lowercase", "Capitalize", "ALL CAPS"]
        self.g1.case = PopUpButton((87, 32, -0, 20), caseList, sizeStyle="small")
        self.g1.case.set(self.case)

        # character set
        charsetList = ["Use any characters", "Use characters in current font", "Use only selected glyphs", "Use only glyphs with mark color:"]
        self.g1.base = PopUpButton((0, 61, -0, 20), charsetList, callback=self.baseChangeCallback, sizeStyle="small")
        if not CurrentFont():
            self.g1.base.set(0)    # Use any
            self.g1.base.enable(False) # Disable selection
        else:
            if self.limitToCharset == False:
                self.g1.base.set(0) # Use any
            else:
                self.g1.base.set(1) # Use current font

        # mark color selection
        self.g1.colorWell = NoneTypeColorWell((-22, 61, -0, 22))
        self.g1.colorWell.set(None)

        # populate from prefs
        if self.reqMarkColor is not "None": # initial pref
            try:
                r, g, b, a = self.reqMarkColor
                savedColor = NSColor.colorWithCalibratedRed_green_blue_alpha_(r, g, b, a)
                self.g1.colorWell.set(savedColor)
            except:
                pass

        if self.g1.base.get() != 3:
            self.g1.colorWell.show(0)


        # Panel 2 - Match letters
        self.g2 = Group((0, 2, 250, 172))

        # Match mode selection
        matchBtnItems = [
           dict(width=40, title="Text", enabled=True),
           dict(width=120, title="GREP pattern match", enabled=True)
           ]
        self.g2.matchMode = SegmentedButton((50, 5, -0, 20), matchBtnItems, callback=self.switchMatchModeCallback, sizeStyle="small")
        rePanelOn = 1 if self.matchMode == "grep" else 0
        self.g2.matchMode.set(rePanelOn)

        # Text/List match mode
        self.g2.textMode = Box((padd,29,-padd,133))

        labelY = [2, 42]
        labelText = ["Require these letters in each word:", "Require one per group in each word:"]
        for i in range(2):
            setattr(self.g2.textMode, "reqLabel%s" % i, TextBox((bPadd, labelY[i], -bPadd, 22), labelText[i], sizeStyle="small"))
        self.g2.textMode.mustLettersBox = EditText((bPadd+2, 18, -bPadd, 19), text=", ".join(self.requiredLetters), sizeStyle="small")
        ### consider using a subclass that allows copy-pasting of glyphs to glyphnames
        y2 = 37
        attrNameTemplate = "group%sbox"
        for i in range(3):
            j = i+1
            y2 += 20
            optionsList = ["%s: %s" % (key, ", ".join(value)) for key, value in self.groupPresets]
            if len(self.requiredGroups[i]) > 0 and self.requiredGroups[i][0] != "":
                optionsList.insert(0, "Recent: " + ", ".join(self.requiredGroups[i]))
            attrName = attrNameTemplate % j
            setattr(self.g2.textMode, attrName, ComboBox((bPadd+2, y2, -bPadd, 19), optionsList, sizeStyle="small"))

        groupBoxes = [self.g2.textMode.group1box, self.g2.textMode.group2box, self.g2.textMode.group3box]
        for i in range(3):
            if len(self.requiredGroups[i]) > 0 and self.requiredGroups[i][0] != "":
                groupBoxes[i].set(", ".join(self.requiredGroups[i]))

        # RE match mode
        self.g2.grepMode = Box((padd,29,-padd,133))
        self.g2.grepMode.label = TextBox((bPadd, 2, -bPadd, 22), "Regular expression to match:", sizeStyle="small")
        self.g2.grepMode.grepBox = EditText((bPadd+2, 18, -bPadd, 19), text=self.matchPattern, sizeStyle="small")

        splainstring = u"This uses Python’s internal re parser.\nExamples:\nf[bhkl] = words with f followed by b, h, k, or l\n.+p.+ = words with p inside them\n^t.*n{2}$ = words starting with t, ending in nn"

        self.g2.grepMode.explainer = TextBox((bPadd, 42, -bPadd, 80), splainstring, sizeStyle="mini")
        self.g2.grepMode.refButton = Button((bPadd, 108, -bPadd, 14), "go to syntax reference", sizeStyle="mini", callback=self.loadREReference)
        self.g2.grepMode.show(0)

        self.toggleMatchModeFields() # switch to text or grep panel depending

        # Panel 3 - Options
        self.g3 = Group((padd, 5, groupW, 48))
        self.g3.checkbox0 = CheckBox((bPadd, 2, 18, 18), "", sizeStyle="small", value=self.banRepetitions)
        self.g3.checkLabel = TextBox((18, 4, -bPadd, 18), "No repeating characters per word", sizeStyle="small")
        self.g3.listOutput = CheckBox((bPadd, 18, 18, 18), "", sizeStyle="small")
        self.g3.listLabel = TextBox((18, 20, -bPadd, 18), "Output as list sorted by width", sizeStyle="small")

        # Display Accordion View
        accItems = [
           dict(label="Basic settings", view=self.g1, size=104, collapsed=False, canResize=False),
           dict(label="Specify required letters", view=self.g2, size=173, collapsed=False, canResize=False),
           dict(label="Options", view=self.g3, size=48, collapsed=False, canResize=False)
           ]
        self.w.panel1 = Group((0, 0, 250, -35))
        self.w.panel1.accView = AccordionView((0, 0, -0, -0), accItems)

        self.w.submit = Button((padd, -30, -padd, 22), 'make words!', callback=self.makeWords)

        self.w.bind("close", self.windowClose)
        self.w.setDefaultButton(self.w.submit)
        self.w.open()



    def loadPrefs(self):
        """Load the saved preferences into the program."""
        self.requiredLetters = []
        self.requiredGroups = [[], [], []]
        self.banRepetitions = False

        # preset character groups
        self.groupPresets = [
            ["[lc] Ascenders", ["b", "f", "h", "k", "l"]],
            ["[lc] Descenders", ["g", "j", "p", "q", "y"]],
            ["[lc] Ball-and-Stick", ["b", "d", "p", "q"]],
            ["[lc] Arches", ["n", "m", "h", "u"]],
            ["[lc] Diagonals", ["v", "w", "x", "y"]]
        ]

        # define initial values
        initialDefaults = {
            "com.ninastoessinger.word-o-mat.wordCount":      20,
            "com.ninastoessinger.word-o-mat.minLength":      3,
            "com.ninastoessinger.word-o-mat.maxLength":      15,
            "com.ninastoessinger.word-o-mat.case":           0,
            "com.ninastoessinger.word-o-mat.limitToCharset": "True",
            "com.ninastoessinger.word-o-mat.source":         0,
            "com.ninastoessinger.word-o-mat.matchMode":      "text",
            "com.ninastoessinger.word-o-mat.matchPattern":   "",
            "com.ninastoessinger.word-o-mat.markColor":      "None",
        }
        registerExtensionDefaults(initialDefaults)

        # load prefs into variables/properties
        prefsToLoad = {
                "wordCount":    "com.ninastoessinger.word-o-mat.wordCount",
                "minLength":    "com.ninastoessinger.word-o-mat.minLength",
                "maxLength":    "com.ninastoessinger.word-o-mat.maxLength",
                "case":         "com.ninastoessinger.word-o-mat.case",
                "matchMode":    "com.ninastoessinger.word-o-mat.matchMode",
                "matchPattern": "com.ninastoessinger.word-o-mat.matchPattern",
                "reqMarkColor": "com.ninastoessinger.word-o-mat.markColor",
            }
        for variableName, pref in prefsToLoad.items():
            setattr(self, variableName, getExtensionDefault(pref))

        # restore booleans from strings
        limitPref = "com.ninastoessinger.word-o-mat.limitToCharset"
        self.limitToCharset = self.readExtDefaultBoolean(getExtensionDefault(limitPref)) if CurrentFont() else False

        # parse mark color pref
        # print("*** %s" % self.reqMarkColor)
        if self.reqMarkColor is not "None":
            if type(self.reqMarkColor) is tuple:
                self.reqMarkColor = tuple(float(i) for i in self.reqMarkColor)
            else:
                self.reqMarkColor = "None"
        #print("loaded mark color pref: %s" % self.reqMarkColor)

    def baseChangeCallback(self, sender):
        """If the selected base was changed, check if the color swatch needs to be shown/hidden."""
        colorSwatch = 1 if sender.get() == 3 else 0
        self.toggleColorSwatch(colorSwatch)

    def toggleColorSwatch(self, show=1):
        """Toggle display of the mark color swatch."""
        endY = -27 if show == 1 else -0
        self.g1.base.setPosSize((0, 61, endY, 20))
        self.g1.colorWell.show(show)

    def switchMatchModeCallback(self, sender):
        """Check if the UI needs toggling between text/grep mode input fields."""
        self.matchMode = "grep" if sender.get() == 1 else "text"
        self.toggleMatchModeFields()

    def toggleMatchModeFields(self):
        """Toggle between showing text or grep mode input fields."""
        t = self.matchMode == "text"
        g = not t
        self.g2.textMode.show(t)
        self.g2.grepMode.show(g)

    def loadREReference(self, sender):
        """Loads the RE syntax reference in a webbrowser."""
        url = "https://docs.python.org/3.6/library/re.html#regular-expression-syntax"
        webbrowser.open(url, new=2, autoraise=True)

    def readExtDefaultBoolean(self, string):
        """Read a Boolean saved as a string from the prefs."""
        if string == "True":
            return True
        return False

    def writeExtDefaultBoolean(self, var):
        """Write a Boolean to the prefs as a string."""
        if var == True:
            return "True"
        return "False"

    def loadDictionaries(self):
        """Load the available wordlists and read their contents."""
        self.dictWords = {}
        self.allWords = []
        self.outputWords = []

        self.textfiles = ['catalan', 'czech', 'danish', 'dutch', 'ukacd', 'finnish', 'french', 'german', 'hungarian', 'icelandic', 'italian', 'latin', 'norwegian', 'polish', 'slovak', 'spanish', 'vietnamese']
        self.languageNames = ['Catalan', 'Czech', 'Danish', 'Dutch', 'English', 'Finnish', 'French', 'German', 'Hungarian', 'Icelandic', 'Italian', 'Latin', 'Norwegian', 'Polish', 'Slovak', 'Spanish', 'Vietnamese syllables']
        self.source = getExtensionDefault("com.ninastoessinger.word-o-mat.source", 4)

        bundle = ExtensionBundle("word-o-mat")
        contentLimit  = '*****' # If word list file contains a header, start looking for content after this delimiter

        # read included textfiles
        for textfile in self.textfiles:
            path = bundle.getResourceFilePath(textfile)
            with codecs.open(path, mode="r", encoding="utf-8") as fo:
                lines = fo.read()

            self.dictWords[textfile] = lines.splitlines() # this assumes no whitespace has to be stripped

            # strip header
            try:
                contentStart = self.dictWords[textfile].index(contentLimit) + 1
                self.dictWords[textfile] = self.dictWords[textfile][contentStart:]
            except ValueError:
                pass

        # read user dictionary
        with open('/usr/share/dict/words', 'r') as userFile:
            lines = userFile.read()
        self.dictWords["user"] = lines.splitlines()


    def changeSourceCallback(self, sender):
        """On changing source/wordlist, check if a custom word list should be loaded."""
        customIndex = len(self.textfiles) + 2
        if sender.get() == customIndex: # Custom word list
            try:
                filePath = getFile(title="Load custom word list", messageText="Select a text file with words on separate lines", fileTypes=["txt"])[0]
            except TypeError:
                filePath = None
                self.customWords = []
                print("word-o-mat: Input of custom word list canceled, using default")
            if filePath is not None:
                with codecs.open(filePath, mode="r", encoding="utf-8") as fo:
                    lines = fo.read()
                # self.customWords = lines.splitlines()
                self.customWords = []
                for line in lines.splitlines():
                    w = line.strip() # strip whitespace from beginning/end
                    self.customWords.append(w)


    def fontCharacters(self, font):
        """Check which Unicode characters are available in the font."""
        if not font:
            return []
        charset = []
        gnames = []
        for g in font:
            if g.unicode is not None:
                try:
                    charset.append(chr(int(g.unicode)))
                    gnames.append(g.name)
                except ValueError:
                    pass
        return charset, gnames


    # INPUT HANDLING

    def getInputString(self, field, stripColon):
        """Read an input string from a field, and convert it to a list of glyphnames."""
        inputString = field.get()
        pattern = re.compile(" *, *| +")
        if stripColon:
            i = inputString.find(":")
            if i != -1:
                inputString = inputString[i+1:]
        result1 = pattern.split(inputString)

        result2 = []
        for c in result1:
            if len(c)>1: # glyph names
                if self.f is not None:
                    if c in self.f:
                        g = self.f[c]
                        try:
                            value = chr(int(g.unicode))
                            result2.append(value)
                        except TypeError: # unicode not set
                            message ("word-o-mat: Glyph \"%s\" was found, but does not appear to have a Unicode value set. It can therefore not be processed, and will be skipped." % c)
                    else:
                        message ("word-o-mat: Conflict: Character \"%s\" was specified as required, but not found. It will be skipped." % c)
                else:
                        message ("word-o-mat: Sorry, matching by glyph name is only supported when a font is open. Character \"%s\" will be skipped." % c)
            else: # character values
                result2.append(c)
        result = [s for s in result2 if s]
        return result


    def getIntegerValue(self, field):
        """Get an integer value (or if not set, the placeholder) from a field."""
        try:
            returnValue = int(field.get())
        except ValueError:
            returnValue = int(field.getPlaceholder())
            field.set(returnValue)
        return returnValue


    # INPUT CHECKING

    def checkReqVsFont(self, required, limitTo, fontChars, customCharset):
        """Check if a char is required from a font/selection/mark color that doesn't have it."""
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
                    message ("word-o-mat: Conflict: Character \"%s\" was specified as required, but not found in the %s." % (c, messageCharset))
                    return False
            return True


    def checkReqVsLen(self, required, maxLength):
        """Check for conflicts between number of required characters and specified word length.
        Only implemented for text input for now.
        """
        if self.matchMode != "grep":
            if len(required) > maxLength:
                message ("word-o-mat: Conflict: Required characters exceed maximum word length. Please revise.")
                return False
        return True


    def checkReqVsCase(self, required, case):
        """Check that required letters do not contradict case selection.

        This seems to be a frequent source of user error.
        Only implemented for text mode (character list), not grep.
        """

        errNotLower = "word-o-mat: Conflict: You have specified all-lowercase words, but required uppercase characters. Please revise."
        errNotUpper = "word-o-mat: Conflict: You have specified words in ALL CAPS, but required lowercase characters. Please revise."

        if self.matchMode != "grep":

            # all lowercase words -- catch caps
            if case == 1:
                for c in required:
                    if not c.islower():
                        message (errNotLower)
                        return False
                return True

            # all caps -- catch lowercase letters
            elif case == 3:
                for c in required:
                    if not c.isupper():
                        message (errNotUpper)
                        return False
                return True
        return True


    def checkMinVsMax(self, minLength, maxLength):
        """Check user input for minimal/maximal word length and see if it makes sense."""
        if not minLength <= maxLength:
            message ("word-o-mat: Confusing input for minimal/maximal word length. Please fix.")
            return False
        return True


    def checkRE(self):
        """Check if the regular expression entered by the user compiles."""
        if self.matchMode == "grep":
            try:
                self.matchPatternRE = re.compile(self.matchPattern)
                return True
            except re.error:
                self.matchPatternRE = None
                message ("word-o-mat: Could not compile regular expression.")
                return False
        else:
            self.matchPatternRE = None
            return True


    def checkInput(self, limitTo, fontChars, customCharset, required, minLength, maxLength, case):
        """Run the user input through all the individual checking functions."""

        requirements = [
            (self.checkReqVsLen, [required, maxLength]),
            (self.checkReqVsFont, [required, limitTo, fontChars, customCharset]),
            (self.checkReqVsCase, [required, case]),
            (self.checkMinVsMax, [minLength, maxLength]),
            (self.checkRE, []),
        ]
        for reqFunc, args in requirements:
            if not reqFunc(*args):
                return False
        return True


    # OUTPUT SORTING

    def sortWordsByWidth(self, wordlist):
        """Sort output word list by width."""
        f = CurrentFont()
        wordWidths = []

        for word in wordlist:
            unitCount = 0
            for char in word:
                try:
                    glyphWidth = f[char].width
                except:
                    try:
                        gname = self.glyphNamesForValues[char]
                        glyphWidth = f[gname].width
                    except:
                        glyphWidth = 0
                unitCount += glyphWidth
            # add kerning
            for i in range(len(word)-1):
                pair = list(word[i:i+2])
                unitCount += int(self.findKerning(pair))
            wordWidths.append(unitCount)

        wordWidths_sorted, wordlist_sorted = zip(*sorted(zip(wordWidths, wordlist))) # thanks, stackoverflow
        return wordlist_sorted


    def findKerning(self, chars):
        """Helper function to find kerning between two given glyphs.
        This assumes MetricsMachine style group names."""

        markers = ["@MMK_L_", "@MMK_R_"]
        keys = [c for c in chars]

        for i in range(2):
            allGroups = self.f.groups.findGlyph(chars[i])
            if len(allGroups) > 0:
                for g in allGroups:
                    if markers[i] in g:
                        keys[i] = g
                        continue

        key = (keys[0], keys[1])
        if key in self.f.kerning:
            return self.f.kerning[key]
        else:
            return 0


    def makeWords(self, sender=None):
        """Parse user input, save new values to prefs, compile and display the resulting words.

        I think this function is too long and bloated, it should be taken apart. ########
        """

        global warned
        self.f = CurrentFont()

        if self.f is not None:
            self.fontChars, self.glyphNames = self.fontCharacters(self.f)
            self.glyphNamesForValues = {self.fontChars[i]: self.glyphNames[i] for i in range(len(self.fontChars))}
        else:
            self.fontChars = []
            self.glyphNames = []

        self.wordCount = self.getIntegerValue(self.g1.wordCount)
        self.minLength = self.getIntegerValue(self.g1.minLength)
        self.maxLength = self.getIntegerValue(self.g1.maxLength)
        self.case = self.g1.case.get()
        self.customCharset = []

        charset = self.g1.base.get()
        self.limitToCharset = True
        if charset == 0:
            self.limitToCharset = False

        elif charset == 2: # use selection
            if len(self.f.selection) == 0: # nothing selected
                message("word-o-mat: No glyphs were selected in the font window. Will use any characters available in the current font.")
                self.g1.base.set(1) # use font chars
            else:
                try:
                    self.customCharset = []
                    for gname in self.f.selection:
                        if self.f[gname].unicode is not None:
                            try:
                                self.customCharset.append(chr(int(self.f[gname].unicode)))
                            except ValueError:
                                pass
                except AttributeError:
                    pass

        elif charset == 3: # use mark color
            c = self.g1.colorWell.get()

            if c is None:
                pass
            elif c.className() == "NSCachedWhiteColor": # not set, corresponds to mark color set to None
                c = None

            self.customCharset = []
            self.reqMarkColor = (c.redComponent(), c.greenComponent(), c.blueComponent(), c.alphaComponent()) if c is not None else None
            for g in self.f:
                if g.mark == self.reqMarkColor:
                    try:
                        self.customCharset.append(chr(int(g.unicode)))
                    except:
                        pass
            if len(self.customCharset) == 0:
                message("word-o-mat: Found no glyphs that match the specified mark color. Will use any characters available in the current font.")
                self.g1.base.set(1) # use font chars
                self.toggleColorSwatch(0)

        self.matchMode = "text" if self.g2.matchMode.get() == 0 else "grep" # braucht es diese zeile noch?

        self.requiredLetters = self.getInputString(self.g2.textMode.mustLettersBox, False)
        self.requiredGroups[0] = self.getInputString(self.g2.textMode.group1box, True)
        self.requiredGroups[1] = self.getInputString(self.g2.textMode.group2box, True)
        self.requiredGroups[2] = self.getInputString(self.g2.textMode.group3box, True)
        self.matchPattern = self.g2.grepMode.grepBox.get()

        self.banRepetitions = self.g3.checkbox0.get()
        self.outputWords = [] # initialize/empty

        self.source = self.g1.source.get()
        languageCount = len(self.textfiles)
        if self.source == languageCount: # User Dictionary
            self.allWords = self.dictWords["user"]
        elif self.source == languageCount+1: # Use all languages
            for i in range(languageCount):
                # if any language: concatenate all the wordlists
                self.allWords.extend(self.dictWords[self.textfiles[i]])
        elif self.source == languageCount+2: # Custom word list
            try:
                if self.customWords != []:
                    self.allWords = self.customWords
                else:
                    self.allWords = self.dictWords["ukacd"]
                    self.g1.source.set(0)
            except AttributeError:
                self.allWords = self.dictWords["ukacd"]
                self.g1.source.set(0)
        else: # language lists
            for i in range(languageCount):
                if self.source == i:
                    self.allWords = self.dictWords[self.textfiles[i]]

        # store new values as defaults

        markColorPref = self.reqMarkColor if self.reqMarkColor is not None else "None"

        extDefaults = {
            "wordCount": self.wordCount,
            "minLength": self.minLength,
            "maxLength": self.maxLength,
            "case": self.case,
            "limitToCharset": self.writeExtDefaultBoolean(self.limitToCharset),
            "source": self.source,
            "matchMode": self.matchMode,
            "matchPattern": self.matchPattern, # non compiled string
            "markColor": markColorPref,
            }
        for key, value in extDefaults.items():
            setExtensionDefault("com.ninastoessinger.word-o-mat."+key, value)

        # go make words
        if self.checkInput(self.limitToCharset, self.fontChars, self.customCharset, self.requiredLetters, self.minLength, self.maxLength, self.case) == True:

            checker = wordcheck.wordChecker(self.limitToCharset, self.fontChars, self.customCharset, self.requiredLetters, self.requiredGroups, self.matchPatternRE, self.banRepetitions, self.minLength, self.maxLength, matchMode=self.matchMode)

            for i in self.allWords:
                if len(self.outputWords) >= self.wordCount:
                    break
                else:
                    w = choice(self.allWords)
                    if self.case == 1:   w = w.lower()
                    elif self.case == 2:
                        # special capitalization rules for Dutch IJ
                        # this only works when Dutch is selected as language, not "any".
                        try:
                            ijs = ["ij", "IJ", "Ij"]
                            if self.languageNames[self.source] == "Dutch" and w[:2] in ijs:
                                wNew = "IJ" + w[2:]
                                w = wNew
                            else:
                                w = w.title()
                        except IndexError:
                            w = w.title()
                    elif self.case == 3:
                        # special capitalization rules for German double s
                        if u"ß" in w:
                            w2 = w.replace(u"ß", "ss")
                            w = w2
                        w = w.upper()

                    if checker.checkWord(w, self.outputWords):
                        self.outputWords.append(w)

            # output
            if len(self.outputWords) < 1:
                message("word-o-mat: no matching words found <sad trombone>")
            else:
                joinString = " "
                if self.g3.listOutput.get() == True:
                    joinString = "\\n"
                    self.outputWords = self.sortWordsByWidth(self.outputWords)
                outputString = joinString.join(self.outputWords)
                try:
                    sp = OpenSpaceCenter(CurrentFont())
                    sp.setRaw(outputString)
                except:
                    if warned == False:
                        message("word-o-mat: No open fonts found; words will be displayed in the Output Window.")
                    warned = True
                    print("word-o-mat: %s" % outputString)
        else:
            print("word-o-mat: Aborted because of errors")


    def fontClosed(self, info):
        """Check if there are any fonts left open, otherwise disable relevant UI controls."""
        if len(AllFonts()) <= 1:
            self.g1.base.set(0) # use any characters
            self.g1.base.enable(False)

    def windowClose(self, sender):
        """Remove observers when the extension window is closed."""
        removeObserver(self, "fontDidOpen")
        removeObserver(self, "fontWillClose")


OpenWindow(WordomatWindow)
