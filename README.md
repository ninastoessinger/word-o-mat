word-o-mat v2.1
==========

Looking for words that contain "q" but not "u"? Or words that use an "a", a "g", at least one ascender, and one diagonal, but not the ones you haven't drawn yet? This is the sort of thing that word-o-mat can help you with. It's an extension for RoboFont that generates words for use in type sketching, spacing, testing etc.

![word-o-mat screenshot](/screenshot.png)


New in version 2.1:

- Input fields for required characters now accept glyph names as well as character values (so both inputting "ö" or "odieresis" will work).

- Option to output words on separate lines, sorted by length (may be useful for building specimens). This includes kerning, which assumes MetricsMachine-style kern class names (to override this with your own left/right class markers, edit the "markers" list in wordomat.py, line 333).

- Addition of Catalan wordlist, compiled by Joancarles Casasín. Many thanks!


New in version 2.0:

Extended Language Support
=======

- word-o-mat now supports accented characters (should be UTF-8 compliant), so you can also use it for languages other than English (I’ve only tested it for Latin-based languages for now). It uses the Unicode info of the glyphs for this, so make sure you have your codepoints assigned properly.

- Now ships with built-in word lists for: *English*, Czech, Danish, Dutch, Finnish, *French*, *German*, Hungarian, Italian, *Norwegian*, Slovak, and Spanish. Word lists contain approximately 20.000 words each and are derived from lists compiled by Hermit Dave from public/free movie subtitle sources, used with permission and licensed under Creative Commons – Attribution / ShareAlike 3.0. 

Some of the language word lists have been manually checked and corrected:
- German (Nina Stössinger)
- Norwegian (Sindre Bremnes of Monokrom) – https://monokrom.no/
- French (La Police Type Foundry with David Hodgetts) – https://github.com/LaPolice

Others (notably Danish) are in progress. Please help cleaning up the other ones if you can, and use with caution.

You can also still use custom wordlists. (For best results use UTF-8 encoding.)


Reworked Interface
=======

- More compact interface, advanced options hidden by default. Easy switching between languages. 

- The “banned letters” field is gone; in its place I have added an option to use only glyphs that have been selected in the font window. This should be a nicer way to handle proofing a subset of the available glyphs.

- The “randomize output” option has been removed; random output is on by default.

- Different handling of preferences: Required glyphs and groups (hidden pane) will reset to default/empty on startup. Basic options (word count, length, case and language, character set) are (still) saved in the prefs.

- The window is not “always on top” anymore.


If you find any bugs or have suggestions for future development, please get in touch, or fix them yourself :)
