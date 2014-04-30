word-o-mat v2.0
==========

Looking for words that contain "q" but not "u"? Or words that use an "a", a "g", at least one ascender, and one diagonal, but not the ones you haven't drawn yet? This is the sort of thing that word-o-mat can help you with. It's an extension for RoboFont that generates words for use in type sketching, spacing, testing etc.

![word-o-mat screenshot](/screenshot.png)

New in version 2.0:

EXTENDED LANGUAGE SUPPORT

- word-o-mat now supports accented characters (should be UTF-8 compliant), so you can also use it for languages other than English (I’ve only tested it for Latin-based languages for now). It uses the Unicode info of the glyphs for this, so make sure you have your codepoints assigned properly.

- Now ships with built-in word lists for: English, Czech, Danish, Dutch, Finnish, French, German, Hungarian, Italian, Norwegian, Slovak, and Spanish. Word lists contain approximately 20.000 words each and are derived from lists compiled by Hermit Dave from public/free movie subtitle sources, used with permission and licensed under Creative Commons – Attribution / ShareAlike 3.0. 
You can also still use custom wordlists. (For best results use UTF-8 encoding.)

Extended language support is very fresh. I hope to have more comprehensive and less error-prone lists in the future, and expand the list of included languages; your help is welcome and needed. Please report any bugs, as well as words that should be corrected or dropped.


REWORKED INTERFACE

- More compact interface, advanced options hidden by default. Easy switching between languages. 

– The “banned letters” field is gone; in its place I have added an option to use only glyphs that have been selected in the font window. This should be a nicer way to handle proofing a subset of the available glyphs.

– The “randomize output” option has been removed; random output is on by default.

- Different handling of preferences: Required glyphs and groups (hidden pane) will reset to default/empty on startup. Basic options (word count, length, case and language, character set) are (still) saved in the prefs.

- The window is not “always on top” anymore.
=======
This is my first RF extension, supplied without any promises and all that jazz (formally, I’m putting an MIT license on my code; please note the licensing terms of the included word lists, too). Please also note that I assume no responsibility for inappropriate words rendered by this extension.
If you find any bugs or have suggestions for future development, please get in touch, or fix them yourself :)
>>>>>>> FETCH_HEAD

