from typing import Optional, Literal, Union
from collections import OrderedDict

class Ligatures:
    def __init__(self, type: "Literal['ligature']", format: "Literal['unicode']"="unicode", ligatures: "dict" = {}, fonts: "Optional[list[str]]"=None):
        self.type = type
        self.format = format
        self.fonts = fonts
        self.ligatures = {}
        self.ligatures.update(ligatures)
    def __str__(self):
        return f"Ligatures(type='{self.type}', fonts={self.fonts}):\n\t{self.ligatures}"


class Macros:
    def __init__(self, type: "Literal['macro', 'macro + char']", format: "Literal['unicode', 'name']"="unicode", macros: "dict" = {}, fonts: "Optional[list[str]]"=None):
        self.type = type
        self.format = format
        self.fonts = fonts
        self.macros = {}
        self.macros.update(macros)
    def __str__(self):
        return f"Macros(type='{self.type}', fonts={self.fonts}):\n\t{self.macros}"

greek = Macros(type="macro", fonts=["DejaVu Italic"])
greek.macros.update({
    "alpha": "α",
    "beta": "β",
    "gamma": "γ",
    "Gamma": "Γ",
    "delta": "δ",
    "Delta": "Δ",
    "varepsilon": "ε",
    "epsilon": "ϵ",
    "zeta": "ζ",
    "eta": "η",
    "theta": "θ",
    "vartheta": "ϑ",
    "Theta": "Θ",
    "iota": "ι",
    "kappa": "κ",
    "lambda": "λ",
    "Lambda": "Λ",
    "mu": "μ",
    "nu": "ν",
    "xi": "ξ",
    "Xi": "Ξ",
    "pi": "π",
    "Pi": "Π",
    "rho": "ρ",
    "sigma": "σ",
    "Sigma": "Σ",
    "tau": "τ",
    "upsilon": "υ",
    "phi": "ϕ",
    "varphi": "φ",
    "Phi": "Φ",
    "chi": "χ",
    "psi": "ψ",
    "Psi": "Ψ",
    "omega": "ω",
    "Omega": "Ω",
})


misc = Macros(type="macro")
misc.macros.update({
    "infty": "∞",
    "forall": "∀",
    "exists": "∃",
    "nexists": "∄",
    "partial": "∂",
    "emptyset": "∅",
    "cdots": "···",
    "ldots": "...",
    "lceil": "⌈",
    "rceil": "⌉",
    "lfloor": "⌊",
    "rfloor": "⌋"
})

operators = Macros(type="macro")
operators.macros.update({
    "times": "×",
    "cdot": "•",
    "cap": "∩",
    "cup": "∪",
    "neq": "≠",
    "leq": "≤",
    "geq": "≥",
    "in": "∈",
    "notin": "∉",
    "subset": "⊂",
    "supset": "⊃",
    "approx": "≈",
    "equiv": "≡",
    "ll": "≪",
    "gg": "≫"
})

mathbb = Macros(type="macro + char")
mathbb.macros.update({
    "mathbb": {
        "N": "ℕ",
        "Z": "ℤ",
        "Q": "ℚ",
        "R": "ℝ",
        "C": "ℂ",
    }
})

shorthand_NZQRC = Macros(
    type="macro",
    macros={
        "NN": "ℕ",
        "ZZ": "ℤ",
        "QQ": "ℚ",
        "RR": "ℝ",
        "CC": "ℂ"
    })

mathcal = Macros(type="macro + char", macros={"mathcal": {}})
for c in list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
    mathcal.macros["mathcal"][c] = chr(ord(c)-ord('A')+ord("𝓐"))


mathfrak = Macros(type="macro + char", macros={"mathfrak": {}})
for c in list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
    mathfrak.macros["mathfrak"][c] = chr(ord(c)-ord('A')+ord("𝕬"))


map_arrows = Macros(type="macro")
map_arrows.macros.update({
    "to": "⟶",
    "mapsto": "⟼"
})

# Name of the font to add to
MAIN_FONT = "DroidSansMono.ttf"

# Name of the font to create (no extensions and None for default)
OUT_FONT_NAME = "Test"

# Font to add new symbols from (ordered by priority)
FONTS = OrderedDict()
FONTS["Droid Sans Mono"] = "DroidSansMono.ttf"
FONTS["Fira Code"] = "FiraCode-Regular.ttf"
FONTS["Latin Modern"] = "LatinModernMath.otf"
FONTS["DejaVu Bold"] = "DejaVuSansMono-Bold.ttf"
FONTS["DejaVu Italic"] = "DejaVuSansMono-Italic.ttf"

# Alias for commands ( Not default behaviour only e.g. \renewcommand\cal[1]{{\mathcal{#1}}} )
#mathbb.macros["bb"] = mathbb.macros["mathbb"]
mathcal.macros["cal"] = mathcal.macros["mathcal"]
mathfrak.macros["frak"] = mathfrak.macros["mathfrak"]


sup_sub_ligs = Ligatures("ligature", fonts=["Fira Code"])
sup_sub_ligs.ligatures.update({
    "^0": "⁰",
    "^1": "¹",
    "^2": "²",
    "^3": "³",
    "^4": "⁴",
    "^5": "⁵",
    "^6": "⁶",
    "^7": "⁷",
    "^8": "⁸",
    "^9": "⁹",
    "_0": "₀",
    "_1": "₁",
    "_2": "₂",
    "_3": "₃",
    "_4": "₄",
    "_5": "₅",
    "_6": "₆",
    "_7": "₇",
    "_8": "₈",
    "_9": "₉"
})



# Bold greek
custom_b_greek = Macros(type="macro", fonts=["DejaVu Bold"])
for k in list(greek.macros.keys()):
    if k == "eta":
        continue
    custom_b_greek.macros["b"+k] = "b"+chr(ord(greek.macros[k]))

# The ligatures to add to the font
LIGATURES: "list[Union[Macros, Ligatures]]" = [
    greek,
    operators,
    misc,
    mathbb,
    shorthand_NZQRC,
    mathcal,
    mathfrak,
    map_arrows,
    custom_b_greek,
    sup_sub_ligs
]

COPYRIGHT = '\nProgramming ligatures added by Ilya Skriblovsky from FiraCode\nFiraCode Copyright (c) 2015 by Nikita Prokopov'