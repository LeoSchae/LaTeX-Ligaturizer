#!/usr/bin/env python

from sre_constants import LITERAL
import fontforge
import os
from ligatures import ligatures

# Constants
SOURCE_FONT_DIR = "input-fonts"
OUTPUT_FONT_DIR = "output-fonts"
COPYRIGHT = '\nProgramming ligatures added by Ilya Skriblovsky from FiraCode\nFiraCode Copyright (c) 2015 by Nikita Prokopov'

def get_input_fontname():
    return input('Enter the source font filename (including extension): ')

def get_input_path(input_fontname):
    return SOURCE_FONT_DIR + "/" + input_fontname

# "RobotoMono-Regular.ttf" -> "RobotoMono-Regular"
def name_without_file_extension(fontname):
    return fontname[:-4] if fontname.endswith(('.otf', '.ttf')) else fontname

# "RobotoMono-Regular" -> "RobotoMono"
def name_without_width_variant(fontname):
    no_variant = fontname
    if fontname.endswith("Regular"):
        no_variant = fontname[:-7]
    elif fontname.endswith("Book"):
        no_variant = fontname[:-4]
    return no_variant[:-1] if (no_variant.endswith(" ") or no_variant.endswith("-")) else no_variant

def get_output_fontname(input_name):
    new_fontname = input('Enter a name for your ligaturized font -- or press ENTER to use the same name: ')
    if new_fontname == "":
        new_fontname = input_name
    return name_without_width_variant(name_without_file_extension(new_fontname))

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

LETTERS = tuple('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')

class LaTeXLigatureCreator:
    """
    Macros have to be registered with decreasing length. This prevents macros from being overly long.
    """

    def __init__(self, font, ligature_fonts=[]):
        self.font = font
        self.ligature_fonts=ligature_fonts

        self._lookup_count = 0

        self.feature = (('calt', (('DFLT', ('dflt',)), ('arab', ('dflt',)), ('armn', ('dflt',)), ('cyrl', ('SRB ', 'dflt')), ('geor', ('dflt',)), ('grek', ('dflt',)), ('lao ', ('dflt',)), ('latn', ('CAT ', 'ESP ', 'GAL ', 'ISM ', 'KSM ', 'LSM ', 'MOL ', 'NSM ', 'ROM ', 'SKS ', 'SSM ', 'dflt')), ('math', ('dflt',)), ('thai', ('dflt',)))),)
        
        self.macro_length_lookup = "calt.macro.length"
        self._max_macro_len = -1


    def add_glyph_from(self, glyph_name: "str", font, source_glyph: "str"):
        """ Add glyph to this font. Name of the new glyph is `glyph_name`. """
        self.font.createChar(-1, glyph_name)

        font.selection.none()
        font.selection.select(source_glyph)
        font.copy()

        self.font.selection.none()
        self.font.selection.select(glyph_name)
        self.font.paste()

    def add_unicode_glyph_from(self, glyph_name: "str", fonts: "list", unicode_char: "str"):
        """ Add glyph to this font. Name of the new glyph is `glyph_name`.
            `source_glyph` is a single char unicode string """
        for font in fonts:
            glyph = find_unicode_glyph(font, unicode_char)
            if glyph is not None:
                self.add_glyph_from(glyph_name, font, glyph)
                return
        raise Exception("Unicode glyph '{unicode_char}' not found in provided fonts")

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
                self.add_glyph_from(self.macro_glyph(length), font=self.font, source_glyph="backslash")
            
            # Create single sub lookup for macro character
            self.font.addLookup(lookup_name(length), "gsub_single", (), ())
            self.font.addLookupSubtable(lookup_name(length), lookup_sub_name(length))

            self.font["backslash"].addPosSub(lookup_sub_name(length), self.macro_glyph(length))

            # Add contextual lookup
            self.font.addContextualSubtable(
                macro_length_lookup,
                f"lookup.ctx.macro.length.{length}",
                "class",
                f"| 1 @<{lookup_name(length)}> | {' '.join(['1']*length)}",
                bclasses=((), ),
                fclasses=((), LETTERS),
                mclasses=((), ("backslash",))
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
    
    def add_macro(self, macro: "str", replacement: "str"):
        self.lookup_macros(len(macro))

        macro_glyph = self.macro_glyph(len(macro))
        input_chars = list(macro)
        output_chars = []

        glyph_name = lambda i: f"repl.macro.{macro}.{i}"

        for i, char in enumerate(list(replacement)):
            output_chars.append(glyph_name(i))
            self.add_unicode_glyph_from(glyph_name(i), fonts=self.ligature_fonts, unicode_char=char)
        
        self.add_multi_ligature(
            input_chars,
            output_chars,
            look_back=[macro_glyph],
            lookup_feature=self.feature,
            lookup_after="calt.macro.length"
        )
    
    def add_macro_font_single(self, macro: "str", argMap: "dict[str,str]"):
        """ For macros of the form `\mathbb N` or `\mathbb{N}` """
        self.lookup_macros(len(macro))

        macro_glyph = self.macro_glyph(len(macro))
        open_glyph = find_unicode_glyph(self.font, "{")
        close_glyph = find_unicode_glyph(self.font, "}")


        for arg in argMap:
            glyph_name = lambda i: f"repl.macro.{macro}.{arg}.{i}"

            output_chars = []

            for i, char in enumerate(list(argMap[arg])):
                output_chars.append(glyph_name(i))
                self.add_unicode_glyph_from(glyph_name(i), fonts=self.ligature_fonts, unicode_char=char)

            arg_glyph = find_unicode_glyph(self.font, arg)

            # without { }
            in_chars1 = list(macro) + ["space", arg_glyph]
            self.add_multi_ligature(
                in_chars1,
                output_chars,
                look_back=[macro_glyph],
                lookup_feature=self.feature,
                lookup_after="calt.macro.length"
            )

            # with { }
            in_chars2 = list(macro) + [open_glyph, arg_glyph, close_glyph]
            self.add_multi_ligature(
                in_chars2,
                output_chars,
                look_back=[macro_glyph],
                lookup_feature=self.feature,
                lookup_after="calt.macro.length"
            )

    def add_macro2(self, macro: "str", replacement: "str"):
        macro_glyph = self.macro_glyph(len(macro))
        input_chars = list(macro)
        output_chars = []

        glyph_name = lambda i: f"repl.macro.{macro}.{i}"

        for i, char in enumerate(list(replacement)):
            output_chars.append(glyph_name(i))
            for lig_font in self.ligature_fonts:
                repl_glyph = find_unicode_glyph(lig_font, char)
                if(repl_glyph is not None):
                    self.font.createChar(-1, glyph_name(i))
                    lig_font.selection.none()
                    lig_font.selection.select(repl_glyph)
                    lig_font.copy()
                    self.font.selection.none()
                    self.font.selection.select(glyph_name(i))
                    self.font.paste()
                    break
        
        if len(input_chars) < len(output_chars):
            raise Exception("Macro replacement must be shorter than the macro")

        # contextual lookup for macro
        ctx_lookup_name = f"calt.macro.{macro}"
        self.font.addLookup(ctx_lookup_name, 'gsub_contextchain', (), self.feature, "calt.macro.length")

        lookup_name = lambda i: f"lookup.macro.{macro}.{i}"
        lookup_sub_name = lambda i: f"lookup.sub.macro.{macro}.{i}"

        # substitution lookup for i-th chatacter for all but last output
        for i in range(len(output_chars)-1):
            in_char = input_chars[i]
            out_char = output_chars[i]

            self.font.addLookup(lookup_name(i), 'gsub_single', (), (), "calt.macro.length")
            self.font.addLookupSubtable(lookup_name(i), lookup_sub_name(i))
            self.font[in_char].addPosSub(lookup_sub_name(i), out_char)

        # Perform ligature substitution on the last part
        i = len(output_chars)-1
        in_char = input_chars[i]
        out_char = output_chars[i]

        self.font.addLookup(lookup_name(i), 'gsub_ligature', (), (), "calt.macro.length")
        self.font.addLookupSubtable(lookup_name(i), lookup_sub_name(i))
        self.font[output_chars[i]].addPosSub(lookup_sub_name(i), tuple(input_chars[i:]))

        # Create the contextual lookup
        pattern = ' '.join([f"{k} @<{lookup_name(i)}>" for i, k in enumerate(input_chars[:len(output_chars)])]) + " " + ' '.join([f"{c}" for c in input_chars[len(output_chars):]])
        pattern = f"{macro_glyph} | {pattern} | "
        self.font.addContextualSubtable(
                ctx_lookup_name,
                f"calt.sub.macro.{macro}",
                'glyph',
                pattern
            )

def change_font_names(font, fontname, fullname, familyname, copyright_add, unique_id):
    font.fontname = fontname
    font.fullname = fullname
    font.familyname = familyname
    font.copyright += copyright_add
    font.sfnt_names = tuple(
        (row[0], 'UniqueID', unique_id) if row[1] == 'UniqueID' else row
        for row in font.sfnt_names
    )
    
input_fontname = get_input_fontname()
input_font_path = get_input_path(input_fontname)

output_fontname = get_output_fontname(input_fontname)
output_font = get_output_font_details(output_fontname)
font = fontforge.open(input_font_path)
firacode = fontforge.open(config['firacode_ttf'])
firacode.em = font.em

cr = LaTeXLigatureCreator(font, [firacode, font])

for lig_group in ligatures:
    lig_type = lig_group["type"]
    
    if lig_type == "macro":
        macros = lig_group["macros"]
        for macro in macros:
            cr.add_macro(macro, macros[macro])
    elif lig_type == "macro + char":
        macros = lig_group["macros"]
        for macro in macros:
            cr.add_macro_font_single(macro, macros[macro])
    else:
        print(f"Ligature type '{lig_type}' not found!")

change_font_names(font, output_font['fontname'],
                        output_font['fullname'],
                        output_font['familyname'],
                        output_font['copyright_add'],
                        output_font['unique_id'])

# Generate font & move to output directory
output_name = output_font['filename']
output_full_path = OUTPUT_FONT_DIR + "/" + output_name
font.generate(output_name)
os.rename(output_name, output_full_path)
print("Generated ligaturized font %s in %s" % (output_font['fullname'], output_full_path))
