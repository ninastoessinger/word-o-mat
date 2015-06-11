word-o-mat v2.2.5
==========

Looking for words that contain ‘q’ but not ‘u’? Or French words that use an ‘a’, a ‘g’, at least one ascender, and one diagonal, but only the ones you’ve marked green? Or words in which to see a specific letter combination, like ‘fk’ or ‘Yc’? This is the sort of thing that word-o-mat can help you with. It's an extension for RoboFont that generates words for use in type sketching, spacing, testing etc.

![word-o-mat screenshot](/screenshot.png)


New in major version 2.2:

- **GREP pattern matching**: As an alternative to specifying lists of required letters (which is still there and unchanged), word-o-mat now also supports pattern matching with regular expressions for more fine-grained control. (Please make sure your regex does not contradict parameters set in the “Basic settings” panel, as the script does not [yet] cleverly check for such things.)

- **Use mark color to constrain character set** (experimental): Hit the color swatch and select a mark color used in your font (in the color interface, you can find them under Swatches > “RoboFont mark colors”). Word-o-mat will then only use glyphs marked precisely that color. Feedback on this functionality is welcome.

- **Language support**: Additional option to get words in **any** available language (mind that this will be slower). Also new wordlists for Latin, Polish, Icelandic, Vietnamese syllables (the latter is a rather short list, but I thought it may still be useful to include). Implemented correct capitalization of German ß to SS.

- Interface cleanups, improved error handling, bugfixes. I also updated the Help, in case anyone is looking at that :)


Extended Language Support:

- word-o-mat is UTF-8 compliant, so you can also use it for languages other than English (I’ve only tested it for Latin-based languages for now). This uses the Unicode info of the glyphs, so make sure you have your codepoints assigned properly.

- Ships with built-in word lists for: *English*, *Catalan*, Czech, Danish, *Dutch*, Finnish, *French*, *German*, Hungarian, Icelandic, *Italian*, *Latin*, *Norwegian*, Polish, Slovak, Spanish, and Vietnamese syllables. Word lists usually contain between 5.000 and 30.000 words each (only the Vietnamese one is much shorter) and are derived from various open/CC licensed sources; please check the individual files for details. Some of these word lists still contain errors and stray words from other languages; the ones italicized above have been manually checked and fixed: German & Dutch (Nina Stössinger),  Norwegian (Sindre Bremnes of [Monokrom](https://monokrom.no/)), French ([La Police Type Foundry](https://github.com/LaPolice) with David Hodgetts), Catalan ([Joancarles Casasín](https://github.com/casasin)), Italian ([Roberto Arista](https://github.com/roberto-arista)), and Latin which was greatly expanded/improved by [Tobias Frere-Jones](http://www.frerejones.com/). Thanks! – You can also use custom wordlists. (For best results use UTF-8 encoding.) 

If you find any bugs or have suggestions for future development, please get in touch, or fix them yourself :)
