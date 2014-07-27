word-o-mat v2.1
==========

Looking for words that contain "q" but not "u"? Or words that use an "a", a "g", at least one ascender, and one diagonal, but not the ones you haven't drawn yet? This is the sort of thing that word-o-mat can help you with. It's an extension for RoboFont that generates words for use in type sketching, spacing, testing etc.

![word-o-mat screenshot](/screenshot.png)


New in version 2.1:

- Input fields for required characters now accept glyph names as well as character values (so both inputting "ö" or "odieresis" will work).

- Option to output words on separate lines, sorted by length (may be useful for building specimens). This includes kerning, which assumes MetricsMachine-style kern class names (to override this with your own left/right class markers, edit the "markers" list in wordomat.py, line 333).

- Addition of Catalan wordlist, compiled by Joancarles Casasín. Many thanks!


Extended Language Support:

- word-o-mat is UTF-8 compliant, so you can also use it for languages other than English (I’ve only tested it for Latin-based languages for now). This uses the Unicode info of the glyphs, so make sure you have your codepoints assigned properly.

- Ships with built-in word lists for: *English*, *Catalan*, Czech, Danish, Dutch, Finnish, *French*, *German*, Hungarian, Italian, *Norwegian*, Slovak, and Spanish. Word lists contain approximately 20.000 words each and are derived from lists compiled by Hermit Dave from public/free movie subtitle sources, used with permission and licensed under Creative Commons – Attribution / ShareAlike 3.0. 
You can also still use custom wordlists. (For best results use UTF-8 encoding.)
Some of the language word lists have been manually checked and corrected:
- German (Nina Stössinger)
- Norwegian (Sindre Bremnes of Monokrom) – https://monokrom.no/
- French (La Police Type Foundry with David Hodgetts) – https://github.com/LaPolice
- Catalan (Joancarles Casasín) - https://github.com/casasin

Others (notably Danish) are in progress. Please help cleaning up the other ones if you can, and use with caution.

If you find any bugs or have suggestions for future development, please get in touch, or fix them yourself :)
