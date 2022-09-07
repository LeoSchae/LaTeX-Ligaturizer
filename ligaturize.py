#!/usr/bin/env python
import fontforge
import os
from pathlib import Path
from ligatures import Macros, LIGATURES, MAIN_FONT, FONTS, OUT_FONT_NAME, COPYRIGHT
from typing import Literal

config = {
    'firacode_ttf': 'FiraCode-Regular.ttf',
}

def name_from_codepoint(font, unicode_str):
    unicode = ord(unicode_str)
    alt_match = None
    for glyph_name in font:
        glyph = font[glyph_name]
        if glyph.unicode == unicode:
            return glyph_name
        if(glyph.altuni is not None):
            for alt in glyph.altuni:
                if(alt[0] == unicode):
                    alt_match = glyph_name
    return alt_match

def find_unicode_glyph(font, unicode_char):
    """ takes Single character string """
    unicode = ord(unicode_char)
    alt_match = None
    for glyph_name in font:
        glyph = font[glyph_name]
        if glyph.unicode == unicode:
            return glyph_name
        if(glyph.altuni is not None):
            for alt in glyph.altuni:
                if(alt[0] == unicode):
                    alt_match = glyph_name
    return alt_match

def get_output_font_details(fontname):
    name_with_spaces = split_camel_case(fontname)
    return {
        'filename': fontname + '.ttf',
        'fontname': fontname,
        'fullname': name_with_spaces,
        'familyname': name_with_spaces,
        'copyright_add': COPYRIGHT,
        'unique_id': name_with_spaces,
    }

# Add spaces to UpperCamelCase: 'DVCode' -> 'DV Code'
def split_camel_case(str):
    acc = ''
    for (i, ch) in enumerate(str):
        prevIsSpace = i > 0 and acc[-1] == ' '
        nextIsLower = i + 1 < len(str) and str[i + 1].islower()
        isLast = i + 1 == len(str)
        if i != 0 and ch.isupper() and (nextIsLower or isLast) and not prevIsSpace:
            acc += ' ' + ch
        elif ch == '-' or ch == '_' or ch == '.':
            acc += ' '
        else:
            acc += ch
    return acc

def change_font_names(font, fontname, fullname, familyname, copyright_add, unique_id):
    font.fontname = fontname
    font.fullname = fullname
    font.familyname = familyname
    font.copyright += copyright_add
    font.sfnt_names = tuple(
        (row[0], 'UniqueID', unique_id) if row[1] == 'UniqueID' else row
        for row in font.sfnt_names
    )

LETTERS = tuple('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')

class LaTeXLigatureCreator:
    """
    Macros have to be registered with decreasing length. This prevents macros from being overly long.
    """

    def __init__(self, font, source_fonts: "dict"):
        self.font = font
        self.source_fonts = source_fonts

        self.glyph_fonts = {}
        self.glyph_fonts["Default"] = {
            "unicode": {},
            "name": {}
        }
        for k in font:
            self.glyph_fonts["Default"]["name"][k] = k
            if font[k].unicode != -1:
                self.glyph_fonts["Default"]["unicode"][chr(font[k].unicode)] = k

        self._lookup_count = 0

        self.feature = (('calt', (('DFLT', ('dflt',)), ('arab', ('dflt',)), ('armn', ('dflt',)), ('cyrl', ('SRB ', 'dflt')), ('geor', ('dflt',)), ('grek', ('dflt',)), ('lao ', ('dflt',)), ('latn', ('CAT ', 'ESP ', 'GAL ', 'ISM ', 'KSM ', 'LSM ', 'MOL ', 'NSM ', 'ROM ', 'SKS ', 'SSM ', 'dflt')), ('math', ('dflt',)), ('thai', ('dflt',)))),)
        
        self.macro_length_lookup = "calt.macro.length"
        self._max_macro_len = -1

        self.SPACE = self.glyph_fonts["Default"]["unicode"][" "]
        self.BACKSLASH = self.glyph_fonts["Default"]["unicode"]["\\"]
        self.NO_BREAK_SPACE = self.glyph_fonts["Default"]["unicode"][chr(160)]
        self.CURL_OPEN = self.glyph_fonts["Default"]["unicode"]["{"]
        self.CURL_CLOSE = self.glyph_fonts["Default"]["unicode"]["}"]

    def _add_glyph(self, glyph_name: "str", source_glyph: "str", font):
        self.font.createChar(-1, glyph_name)

        font.selection.none()
        font.selection.select(source_glyph)
        font.copy()

        self.font.selection.none()
        self.font.selection.select(glyph_name)
        self.font.paste()

    def use_glyph(self, glyph: "str", fonts: "list[str]"=None, format: "Literal['unicode', 'name']"='unicode') -> "str":
        if fonts is None:
            fonts = ["Default"] + list(self.source_fonts.keys())

        for font_name in fonts:
            if font_name in self.glyph_fonts and glyph in self.glyph_fonts[font_name][format]:
                return self.glyph_fonts[font_name][format][glyph]
            if font_name == "Default":
                continue

            font = self.source_fonts[font_name]
            glyph_name = None
            if format == "unicode":
                glyph_name = find_unicode_glyph(font, glyph)
            elif glyph in font:
                glyph_name = glyph
            
            if glyph_name is not None:
                if font_name not in self.glyph_fonts:
                    self.glyph_fonts[font_name] = {"unicode": {}, "name": {}}

                new_name = "tex."+''.join([c for c in font_name if c.isalpha()])+"."+glyph_name

                self.glyph_fonts[font_name]["name"][glyph_name] = new_name
                if font[glyph_name].unicode != -1:
                    self.glyph_fonts[font_name]["unicode"][chr(font[glyph_name].unicode)] = new_name

                self._add_glyph(new_name, glyph_name, font)
                return new_name
        raise Exception(f"Glyph '{glyph}' (format='{format}') not found in given fonts.")

    def macro_glyph(self, length: "int"):
        return f"macro.{length}.liga"

    def lookup_macros(self, max_len: "int"):
        """ Replaces the '\\' in any macro of length `n` smaller than `max_len` with the glyph `self.macro_glyph(n)`. """

        # Create a lookup if not done so far
        macro_length_lookup = self.macro_length_lookup
        if not macro_length_lookup in self.font.gsub_lookups:
            self.font.addLookup(macro_length_lookup, "gsub_contextchain", (), self.feature)

        lookup_name = lambda i: f"lookup.macro.length.{length}"
        lookup_sub_name = lambda i: f"lookup.sub.macro.length.{length}"

        if max_len <= self._max_macro_len:
            return

        # Add contextual lookup for all length values (if not done so far)
        for length in range(self._max_macro_len+2,max_len+2):

            if not self.macro_glyph(length) in self.font:
                self._add_glyph(self.macro_glyph(length), source_glyph=self.BACKSLASH, font=self.font)
            
            # Create single sub lookup for macro character
            self.font.addLookup(lookup_name(length), "gsub_single", (), ())
            self.font.addLookupSubtable(lookup_name(length), lookup_sub_name(length))

            self.font[self.BACKSLASH].addPosSub(lookup_sub_name(length), self.macro_glyph(length))

            # Add contextual lookup
            self.font.addContextualSubtable(
                macro_length_lookup,
                f"lookup.ctx.macro.length.{length}",
                "class",
                f"| 1 @<{lookup_name(length)}> | {' '.join(['1']*length)}",
                bclasses=((), ),
                fclasses=((), LETTERS),
                mclasses=((), (self.BACKSLASH,))
            )
        
        self._max_macro_len = max_len
    
    def add_multi_ligature(self,
            char_in: "list(str)",
            char_out: "list(str)",
            look_back: "list(str)" = [],
            look_ahead: "list(str)" = [],
            lookup_feature=(),
            lookup_after=None
        ):
        if(len(char_in) < len(char_out)):
            raise Exception("Can only replace by shorter sequence")
        lookup_number = self._lookup_count
        self._lookup_count = self._lookup_count + 1

        ctx_lookup_name = f"lookup.ctx.N{lookup_number}"
        ctx_lookup_sub_name = f"lookup.ctx.sub.N{lookup_number}"
        lookup_name = lambda i : f"lookup.N{lookup_number}.{i}"
        lookup_sub_name = lambda i : f"lookup.sub.N{lookup_number}.sub.{i}"

        # Lookups for all but last char
        for i in range(len(char_out) - 1):
            self.font.addLookup(lookup_name(i), 'gsub_single', (), (), "calt.macro.length")
            self.font.addLookupSubtable(lookup_name(i), lookup_sub_name(i))
            self.font[char_in[i]].addPosSub(lookup_sub_name(i), char_out[i])

        # Lookup for last char
        i = len(char_out)-1
        self.font.addLookup(lookup_name(i), 'gsub_ligature', (), (), "calt.macro.length")
        self.font.addLookupSubtable(lookup_name(i), lookup_sub_name(i))
        self.font[char_out[i]].addPosSub(lookup_sub_name(i), tuple(char_in[i:]))

        # Call lookups from context
        main_patern = ' '.join(f"{char_in[i]} @<{lookup_name(i)}>" for i in range(len(char_out))) + ' '.join([f"{c}" for c in char_in[len(char_out):]])
        pattern = f"{' '.join(look_back)} | {main_patern} | {' '.join(look_ahead)}"
        
        if lookup_after is None:
            self.font.addLookup(ctx_lookup_name, 'gsub_contextchain', (), lookup_feature)
        else:
            self.font.addLookup(ctx_lookup_name, 'gsub_contextchain', (), lookup_feature, lookup_after)
        self.font.addContextualSubtable(
                ctx_lookup_name,
                ctx_lookup_sub_name,
                'glyph',
                pattern
            )
    
    def add_simple_ligature(self, characters: "str", ligature: "str", fonts=None):
        lookup_number = self._lookup_count
        self._lookup_count = self._lookup_count + 1

        lig_glyph = self.use_glyph(ligature, fonts, 'unicode')
        lig_characters = [self.use_glyph(c, ["Default"], "unicode") for c in list(characters)]

        lookup_name = f"lookup.N{lookup_number}.0"
        lookup_sub_name = f"lookup.sub.N{lookup_number}.sub.0"

        self.font.addLookup(lookup_name, 'gsub_ligature', (), self.feature, "calt.macro.length")
        self.font.addLookupSubtable(lookup_name, lookup_sub_name)
        self.font[lig_glyph].addPosSub(lookup_sub_name, lig_characters)

    def add_macro(self, macro: "str", replacement: "str", fonts=None):
        self.lookup_macros(len(macro))

        macro_glyph = self.macro_glyph(len(macro))
        input_chars = list(macro)
        output_chars = []

        for char in list(replacement):
            output_chars.append(self.use_glyph(char, fonts, "unicode"))
        
        self.add_multi_ligature(
            [macro_glyph]+input_chars,
            [self.BACKSLASH]+output_chars,
            look_back=[],
            lookup_feature=self.feature,
            lookup_after="calt.macro.length"
        )
    
    def add_macro_font_single(self, macro: "str", argMap: "dict[str,str]", fonts=None):
        """ For macros of the form `\mathbb N` or `\mathbb{N}` """
        self.lookup_macros(len(macro))

        macro_glyph = self.macro_glyph(len(macro))


        for arg in argMap:
            output_chars = []

            for char in list(argMap[arg]):
                output_chars.append(self.use_glyph(char, fonts, "unicode"))

            arg_glyph = find_unicode_glyph(self.font, arg)

            # without { }
            in_chars1 = list(macro) + [self.SPACE, arg_glyph]
            self.add_multi_ligature(
                [macro_glyph]+in_chars1,
                [self.BACKSLASH]+output_chars,
                look_back=[],
                lookup_feature=self.feature,
                lookup_after="calt.macro.length"
            )

            in_chars1 = list(macro) + [self.NO_BREAK_SPACE, arg_glyph]
            self.add_multi_ligature(
                [macro_glyph]+in_chars1,
                [self.BACKSLASH]+output_chars,
                look_back=[],
                lookup_feature=self.feature,
                lookup_after="calt.macro.length"
            )

            # with { }
            in_chars2 = list(macro) + [self.CURL_OPEN, arg_glyph, self.CURL_CLOSE]
            self.add_multi_ligature(
                [macro_glyph]+in_chars2,
                [self.BACKSLASH]+output_chars,
                look_back=[],
                lookup_feature=self.feature,
                lookup_after="calt.macro.length"
            )


input_folder = Path("input_files/")
out_folder = Path("output_files/")

main_font = fontforge.open((input_folder / MAIN_FONT).as_posix())

source_fonts = {}
for font_name in FONTS:
    f = fontforge.open((input_folder / FONTS[font_name]).as_posix())
    f.em = main_font.em
    source_fonts[font_name] = f

output_font_details = get_output_font_details(OUT_FONT_NAME)

cr = LaTeXLigatureCreator(main_font, source_fonts)

for ligatures in LIGATURES:
    ligature_type = ligatures.type
    print(ligature_type)
    # Treat differently depending on type
    if ligature_type.startswith("macro"):
        fonts = ligatures.fonts
        glyph_format = ligatures.format
        macros = ligatures.macros

        if ligature_type == "macro":
            for macro in macros:
                cr.add_macro(macro, macros[macro], fonts=fonts)

        elif ligature_type == "macro + char":
            for macro in macros:
                cr.add_macro_font_single(macro, macros[macro], fonts=fonts)
                
        else:
            raise Exception(f"Invalid ligature type {ligature_type}")

    elif ligature_type.startswith("ligature"):
        fonts = ligatures.fonts
        lig_dict = ligatures.ligatures
        for chars in lig_dict:
            cr.add_simple_ligature(chars, lig_dict[chars], fonts=fonts)
    else:
        raise Exception(f"Invalid ligature type {ligature_type}")

change_font_names(main_font, output_font_details['fontname'],
                        output_font_details['fullname'],
                        output_font_details['familyname'],
                        output_font_details['copyright_add'],
                        output_font_details['unique_id'])

# Generate font & move to output directory
output_name = output_font_details['filename']
output_full_path = out_folder / output_name
main_font.generate(output_name)
os.rename(output_name, output_full_path)
print("Generated ligaturized font %s in %s" % (output_font_details['fullname'], output_full_path))
