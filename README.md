word-o-mat v2.2
==========

Looking for words that contain "q" but not "u"? Or words that use an "a", a "g", at least one ascender, and one diagonal, but not the ones you haven't drawn yet? This is the sort of thing that word-o-mat can help you with. It's an extension for RoboFont that generates words for use in type sketching, spacing, testing etc.

![word-o-mat screenshot](/screenshot.png)


New in version 2.2:

- **GREP pattern matching**: As an alternative to specifying lists of required letters, word-o-mat now supports pattern matching with regular expressions for more fine-grained control. (Please make sure your regex does not contradict parameters set in the “Basic settings” panel, as the script does not [yet] cleverly check for such things.)

- **Use mark color to constrain character set** (experimental): Hit the color swatch and select a mark color used in your font (in the color interface, you can find them under Swatches > “RoboFont mark colors”). Word-o-mat will then only use glyphs marked precisely that color. Feedback on this functionality is welcome.

- **Language support**: Additional option to get words in **any** available language (mind that this will be slower); new wordlists for Latin, Polish, Icelandic, Vietnamese syllables (the latter is a rather short list, but I thought it may still be useful to include); implemented correct capitalization of German ß (to SS).

- Interface cleanups, improved error handling, bugfixes. I also updated the Help, in case anyone is looking at that :)


New in version 2.1:

- Input fields for required characters now accept glyph names as well as character values (so either inputting "ö" or "odieresis" will work - you can even mix them).

- Option to output words on separate lines, sorted by their calculated set width (may be useful for building specimens). This includes kerning, which assumes MetricsMachine-style kern class names (to override this with your own left/right class markers, edit the "markers" list in wordomat.py, line 333).

- Addition of Catalan wordlist, compiled by Joancarles Casasín. Many thanks!


Extended Language Support:

- word-o-mat is UTF-8 compliant, so you can also use it for languages other than English (I’ve only tested it for Latin-based languages for now). This uses the Unicode info of the glyphs, so make sure you have your codepoints assigned properly.

- Ships with built-in word lists for: *English*, *Catalan*, Czech, Danish, *Dutch*, Finnish, *French*, *German*, Hungarian, Italian, *Norwegian*, Slovak, and Spanish. Word lists contain approximately 20.000 words each and are derived from lists compiled by Hermit Dave from public/free movie subtitle sources, used with permission and licensed under Creative Commons – Attribution / ShareAlike 3.0. 
You can also still use custom wordlists. (For best results use UTF-8 encoding.)
Some of the language word lists have been manually checked and corrected:
- German, Dutch (Nina Stössinger)
- Norwegian (Sindre Bremnes of Monokrom) – https://monokrom.no/
- French (La Police Type Foundry with David Hodgetts) – https://github.com/LaPolice
- Catalan (Joancarles Casasín) - https://github.com/casasin

Others (notably Danish) are in progress. Please help cleaning up the other ones if you can, and use with caution.

If you find any bugs or have suggestions for future development, please get in touch, or fix them yourself :)
