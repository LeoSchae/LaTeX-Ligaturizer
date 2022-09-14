#!/usr/bin/env python
from collections import OrderedDict
import fontforge
import os
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

def name_from_codepoint(font, unicode_str):
    unicode = ord(unicode_str)
    alt_match = None
    for glyph_name in font:
        glyph = font[glyph_name]
        if glyph.unicode == unicode:
            return glyph_name
        if (glyph.altuni is not None):
            for alt in glyph.altuni:
                if (alt[0] == unicode):
                    alt_match = glyph_name
    return alt_match


def find_unicode_glyph(font, unicode_char) -> Optional[str]:
    """ takes Single character string """
    unicode = ord(unicode_char)
    alt_match = None
    for glyph_name in font:
        glyph = font[glyph_name]
        if glyph.unicode == unicode:
            return glyph_name
        if (glyph.altuni is not None):
            for alt in glyph.altuni:
                if (alt[0] == unicode):
                    alt_match = glyph_name
    return alt_match


def split_camel_case(str):
    """ Add spaces to UpperCamelCase: 'DVCode' -> 'DV Code' """
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


class _EditorBackend:
    def __init__(self, font, other_fonts):
        self.font = font
        self.source_fonts: dict[str, Any] = other_fonts

        """
        Dict mapping glyphs to their names.
        Use `useable_glyphs[FONT_NAME][FORMAT][GLYPH]` where `FORMAT` is "unicode" or "name"
        and `GLYPH` is single character unicode string or the glyph name.
        """
        self.useable_glyphs: dict[str,
                                  dict[Literal["unicode", "name"], dict[str, str]]] = {}
        self.useable_glyphs["Default"] = {
            "unicode": {},
            "name": {}
        }
        for k in font:
            self.useable_glyphs["Default"]["name"][k] = k
            if font[k].unicode != -1:
                self.useable_glyphs["Default"]["unicode"][chr(
                    font[k].unicode)] = k

        self.feature = (('calt', (('DFLT', ('dflt',)), ('arab', ('dflt',)), ('armn', ('dflt',)), ('cyrl', ('SRB ', 'dflt')), ('geor', ('dflt',)), ('grek', ('dflt',)), ('lao ',
                        ('dflt',)), ('latn', ('CAT ', 'ESP ', 'GAL ', 'ISM ', 'KSM ', 'LSM ', 'MOL ', 'NSM ', 'ROM ', 'SKS ', 'SSM ', 'dflt')), ('math', ('dflt',)), ('thai', ('dflt',)))),)

        # Special glyph names
        self.SPACE = self.useable_glyphs["Default"]["unicode"][" "]
        self.BACKSLASH = self.useable_glyphs["Default"]["unicode"]["\\"]
        self.NO_BREAK_SPACE = self.useable_glyphs["Default"]["unicode"][chr(
            160)]
        self.CURL_OPEN = self.useable_glyphs["Default"]["unicode"]["{"]
        self.CURL_CLOSE = self.useable_glyphs["Default"]["unicode"]["}"]
        # Macros
        self.macro_length_lookup = "calt.macro.length"

    def add_glyph_manually(self, glyph_name: "str", source_glyph: "str", font):
        """
        Add a new glyph to the font. The added glyph has name `glyph_name` and if taken from `font[source_glyph]`.
        """
        self.font.createChar(-1, glyph_name)

        font.selection.none()
        font.selection.select(source_glyph)
        font.copy()

        self.font.selection.none()
        self.font.selection.select(glyph_name)
        self.font.paste()

    def use_glyph(self, glyph: str, *, fonts: Optional[List[str]] = None, format: Literal["unicode", "name"] = "unicode"):
        if fonts is None:
            fonts = ["Default"] + list(self.source_fonts.keys())
        
        for font_name in fonts:
            if font_name in self.useable_glyphs and glyph in self.useable_glyphs[font_name][format]:
                return self.useable_glyphs[font_name][format][glyph]
            if font_name == "Default":
                continue

            font = self.source_fonts[font_name]
            glyph_name = None
            if format == "unicode":
                glyph_name = find_unicode_glyph(font, glyph)
            elif glyph in font:
                glyph_name = glyph

            if glyph_name is not None:
                if font_name not in self.useable_glyphs:
                    self.useable_glyphs[font_name] = {
                        "unicode": {}, "name": {}}

                new_name = "tex." + \
                    ''.join([c for c in font_name if c.isalpha()]) + \
                    "."+glyph_name

                self.useable_glyphs[font_name]["name"][glyph_name] = new_name
                if font[glyph_name].unicode != -1:
                    self.useable_glyphs[font_name]["unicode"][chr(
                        font[glyph_name].unicode)] = new_name

                self.add_glyph_manually(new_name, glyph_name, font)
                return new_name
        raise Exception(
            f"Glyph '{glyph}' (format='{format}') not found in given fonts.")

    def use_glyph_format(self, glyphs: str, *, fonts: Optional[List[str]] = None, format: Literal["unicode", "advanced"] = "unicode") -> List[str]:
        """
        unicode: parses the string of unicode characters directly.
        advanced: pass glyphs as space separated glyph names. One may specify a font per glyph directly usign "GLYPH_NAME@FONT_NAME".
        """
        glyph_list = []

        if format == "unicode":
            for char in list(glyphs):
                glyph_list.append(self.use_glyph(char, fonts=fonts))
        elif format == "advanced":
            name_list = glyphs.split(" ")
            for glyph_name in name_list:
                split_name = glyph_name.split("*", maxsplit=1)
                # add glyph from default fonts. else use the font specified after *
                if len(split_name) == 1:
                    glyph_list.append(self.use_glyph(
                        split_name[0], format="name", fonts=fonts))
                else:
                    glyph_list.append(self.use_glyph(
                        split_name[0], fonts=[split_name[1]], format="name"))
        else:
            raise Exception("Unknown format")
        return glyph_list

    def add_advanced_ligature(
        self,
        char_in: List[str],
        char_out: List[str],
        *,
        lookup_name=None,
        look_back: List[str] = [],
        look_ahead: List[str] = [],
        lookup_feature=(),
        lookup_after=None
    ):
        if (len(char_in) < len(char_out)):
            raise Exception("Can only replace by shorter sequence")
        if not hasattr(self, "_lookup_count"):
            self._lookup_count = 0
        lookup_number = self._lookup_count
        self._lookup_count = self._lookup_count + 1

        ctx_lookup_name = f"lookup.ctx.N{lookup_number}" if lookup_name is None else lookup_name
        ctx_lookup_sub_name = f"lookup.ctx.sub.N{lookup_number}"
        def gsub_lookup_name(i): return f"lookup.N{lookup_number}.{i}"
        def gsub_lookup_sub_name(
            i): return f"lookup.sub.N{lookup_number}.sub.{i}"

        # Lookups for all but last char
        for i in range(len(char_out) - 1):
            self.font.addLookup(gsub_lookup_name(
                i), 'gsub_single', (), (), "calt.macro.length")
            self.font.addLookupSubtable(
                gsub_lookup_name(i), gsub_lookup_sub_name(i))
            self.font[char_in[i]].addPosSub(
                gsub_lookup_sub_name(i), char_out[i])

        # Lookup for last char
        i = len(char_out)-1
        self.font.addLookup(gsub_lookup_name(
            i), 'gsub_ligature', (), (), "calt.macro.length")
        self.font.addLookupSubtable(
            gsub_lookup_name(i), gsub_lookup_sub_name(i))
        self.font[char_out[i]].addPosSub(
            gsub_lookup_sub_name(i), tuple(char_in[i:]))

        # Call lookups from context
        main_patern = ' '.join(f"{char_in[i]} @<{gsub_lookup_name(i)}>" for i in range(
            len(char_out))) + ' '.join([f"{c}" for c in char_in[len(char_out):]])
        pattern = f"{' '.join(look_back)} | {main_patern} | {' '.join(look_ahead)}"

        if lookup_after is None:
            self.font.addLookup(
                ctx_lookup_name, 'gsub_contextchain', (), lookup_feature)
        else:
            self.font.addLookup(
                ctx_lookup_name, 'gsub_contextchain', (), lookup_feature, lookup_after)
        self.font.addContextualSubtable(
            ctx_lookup_name,
            ctx_lookup_sub_name,
            'glyph',
            pattern
        )

    ## MACROS ##
    def macro_glyph_name(self, length: "int"):
        return f"macro.{length}.liga"

    # The heavy lifting for macros is done here
    def lookup_macros(self, max_len: "int"):
        """ Replaces the '\\' in any macro of length `n` smaller than `max_len` with the glyph `self.macro_glyph_name(n)`. """

        # Create a lookup if not done so far
        macro_length_lookup = self.macro_length_lookup
        if not macro_length_lookup in self.font.gsub_lookups:
            self.font.addLookup(macro_length_lookup,
                                "gsub_contextchain", (), self.feature)

        def lookup_name(i): return f"lookup.macro.length.{length}"
        def lookup_sub_name(i): return f"lookup.sub.macro.length.{length}"

        if not hasattr(self, "_max_macro_len"):
            self._max_macro_len = -1
        if max_len <= self._max_macro_len:
            return

        # Add contextual lookup for all length values (if not done so far)
        for length in range(self._max_macro_len+2, max_len+2):

            if not self.macro_glyph_name(length) in self.font:
                self.add_glyph_manually(self.macro_glyph_name(
                    length), source_glyph=self.BACKSLASH, font=self.font)

            # Create single sub lookup for macro character
            self.font.addLookup(lookup_name(length), "gsub_single", (), ())
            self.font.addLookupSubtable(
                lookup_name(length), lookup_sub_name(length))

            self.font[self.BACKSLASH].addPosSub(
                lookup_sub_name(length), self.macro_glyph_name(length))

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

    def add_macro(self, macro: "str", replacement: "str", *, fonts: Optional[List[str]] = None, repl_format: Literal['unicode', 'advanced'] = "unicode"):
        self.lookup_macros(len(macro))

        input_chars = [self.macro_glyph_name(
            len(macro))] + self.use_glyph_format(macro, format="unicode")
        output_chars = [self.BACKSLASH] + self.use_glyph_format(replacement, fonts=fonts, format=repl_format)

        self.add_advanced_ligature(
            input_chars,
            output_chars,
            lookup_feature=self.feature,
            lookup_after=self.macro_length_lookup
        )

    def add_macro_font(self, macro: "str", map: "dict[str,str]", *, fonts=None, repl_format: Literal['unicode', 'advanced'] = "unicode"):
        """ For macros of the form `\mathbb N` or `\mathbb{N}` """
        self.lookup_macros(len(macro))

        macro_glyph = self.macro_glyph_name(len(macro))

        for character, replacement in map.items():

            char_in = [macro_glyph] + \
                self.use_glyph_format(macro, fonts=["Default"])
            char_out = [self.BACKSLASH] + \
                self.use_glyph_format(
                    replacement, fonts=fonts, format=repl_format)

            arg_glyph: str = self.use_glyph(character, fonts=["Default"])

            # without { }
            self.add_advanced_ligature(
                char_in+[self.SPACE, arg_glyph],
                char_out,
                lookup_feature=self.feature,
                lookup_after=self.macro_length_lookup
            )
            self.add_advanced_ligature(
                char_in+[self.NO_BREAK_SPACE, arg_glyph],
                char_out,
                lookup_feature=self.feature,
                lookup_after=self.macro_length_lookup
            )

            # with { }
            self.add_advanced_ligature(
                char_in+[self.CURL_OPEN, arg_glyph, self.CURL_CLOSE],
                char_out,
                lookup_feature=self.feature,
                lookup_after=self.macro_length_lookup
            )


Glyph_Format = Literal["unicode", "advanced"]

class EditFont:
    def __init__(self, font: str, *, other_fonts: Dict[str, str] = {}, in_folder: str="input_files", out_folder: str="output_files"):
        self.in_folder = Path(in_folder)
        self.out_folder = Path(out_folder)

        self.font = fontforge.open((self.in_folder / font).as_posix())
        _other_fonts = OrderedDict()
        for k, v in other_fonts.items():
            _other_fonts[k] = fontforge.open((self.in_folder / v).as_posix())

        self.backend = _EditorBackend(self.font, _other_fonts)
        

    def add_ligature(
            self, characters: str, ligature: str, *,
            fonts: Optional[List[str]] = None,
            char_format: Glyph_Format = "unicode",
            repl_format: Glyph_Format = "unicode"
        ):
        self.backend.add_advanced_ligature(
            self.backend.use_glyph_format(characters, fonts=["Default"], format=char_format),
            self.backend.use_glyph_format(ligature, fonts=fonts, format=repl_format),
            lookup_feature=self.backend.feature
        )

    def add_ligatures(
            self, ligatures: dict, *,
            char_prefix="",
            char_suffix="",
            lig_prefix="",
            lig_suffix="",
            fonts: Optional[List[str]] = None,
            char_format: Glyph_Format = "unicode",
            repl_format: Glyph_Format = "unicode"
        ):
        for characters, ligature in ligatures.items():
            self.add_ligature(char_prefix + characters + char_suffix, lig_prefix + ligature + lig_suffix, fonts=fonts, char_format=char_format, repl_format=repl_format)

    def add_macro(self, macro: str, replacement: str, *, fonts: Optional[List[str]] = None, repl_format: Glyph_Format="unicode"):
        self.backend.add_macro(macro, replacement, fonts=fonts, repl_format=repl_format)

    def add_macros(self, macros: dict, *, macro_prefix="", macro_suffix="", repl_prefix="", repl_suffix="", fonts: Optional[List[str]] = None, repl_format: Glyph_Format="unicode"):
        for macro, replacement in macros.items():
            self.add_macro(
                macro_prefix + macro + macro_suffix,
                repl_prefix+replacement+repl_suffix,
                fonts=fonts,
                repl_format=repl_format
            )

    def add_macro_font(self, macro: str, map: dict, *, repl_prefix="", repl_suffix="", repl_format: Glyph_Format="unicode", fonts: Optional[List[str]] = None):
        parsed_map = {}
        for k, v in map.items():
            parsed_map[k] = repl_prefix+v+repl_suffix
        self.backend.add_macro_font(macro, parsed_map, fonts=fonts, repl_format=repl_format)
    
    def save(self, camel_name: str, *, file_name: Optional[str]=None, add_copyright: Optional[str]=None):
        # Change font details
        name_with_space = split_camel_case(camel_name)
        if file_name is None:
            file_name = f"{camel_name}.ttf"
        
        self.font.fontname = camel_name
        self.font.fullname = name_with_space
        self.font.familyname = name_with_space
        if add_copyright is not None:
            self.font.copyright += "\n"+add_copyright
        # change only the UniqueID in sfnt names
        self.font.sfnt_names = tuple((row[0], 'UniqueID', name_with_space) if row[1] == 'UniqueID' else row for row in self.font.sfnt_names)

        # Generate font & move to output directory
        output_full_path = self.out_folder / file_name
        self.font.generate(file_name)
        os.rename(file_name, output_full_path)
        print(f"Generated ligaturized font {name_with_space} in {output_full_path.as_posix()}")
        


LETTERS = tuple('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')