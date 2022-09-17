from collections import OrderedDict
from ligaturize import EditFont

LOWER_CASE = [chr(ord("a")+i) for i in range(26)]
UPPER_CASE = [chr(ord("A")+i) for i in range(26)]
ALPHABETIC = LOWER_CASE + UPPER_CASE

font = EditFont(
    font="DroidSansMono.ttf",
    # Other fonts ordered by priority. If a symbol is not found the next font is used.
    other_fonts=OrderedDict([
        ("FiraCode",      "FiraCode-Regular.ttf"),
        ("LatinModern",   "LatinModernMath.otf"),
        ("DejaVu_Bold",   "DejaVuSansMono-Bold.ttf"),
        ("DejaVu_Italic", "DejaVuSansMono-Italic.ttf")
    ])
)

greek_map = {
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
}

# fonts: (prefix_fonts, replacement_fonts, suffix_fonts)
font.add_macros(greek_map, fonts=(None, ["DejaVu_Italic"], None), repl_prefix="\\")


font.add_macros({
    "infty": "∞",
    "forall": "∀",
    "exists": "∃",
    "nexists": "∄",
    "partial": "∂",
    "emptyset": "∅",
    "cdots": "···",
    "ldots": "…"
}, repl_prefix="\\")

font.add_macros({
    "lVert": "l‖",
    "rVert": "r‖",
    "langle": "⟨",
    "rangle": "⟩",
    "lceil": "⌈",
    "rceil": "⌉",
    "lfloor": "⌊",
    "rfloor": "⌋"
}, repl_prefix="\\")

font.add_macros({
    "sum": "summation*FiraCode",
    "prod": "product*FiraCode",
    "int": "integral*FiraCode"
}, repl_prefix="backslash", repl_format="advanced")

font.add_macros({
    "pm": "±",
    "mp": "∓",
    "times": "×",
    "cdot": "•",
    "circ": "∘",
    "odot": "⊙",
    "otimes": "⊗",
    "oplus": "⊕",
    "ominus": "⊖",
    "cap": "∩",
    "cup": "∪",
    "vee": "∨",
    "wedge": "∧",
    "neq": "≠",
    "leq": "≤",
    "geq": "≥",
    "in": "∈",
    "ni": "∋",
    "notin": "∉",
    "subset": "⊂",
    "supset": "⊃",
    "approx": "≈",
    "equiv": "≡",
    "ll": "≪",
    "gg": "≫",
    "perp": "⟂"
}, repl_prefix="\\", fonts=["FiraCode", "Default", "LatinModern"])

font.add_macro_font("mathbb", {
        "N": "ℕ",
        "Z": "ℤ",
        "Q": "ℚ",
        "R": "ℝ",
        "C": "ℂ",
        "P": "ℙ"
    }, repl_prefix="\\", fonts=["FiraCode"])

font.add_macros({
        "NN": "ℕ",
        "ZZ": "ℤ",
        "QQ": "ℚ",
        "RR": "ℝ",
        "CC": "ℂ",
        "PP": "ℙ"
    }, repl_prefix="\\", fonts=["FiraCode"])

mathcal_map = {}
for c in list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
    mathcal_map[c] = chr(ord(c)-ord('A')+ord("𝓐"))
font.add_macro_font("mathcal", mathcal_map, repl_prefix="\\")
font.add_macro_font("cal", mathcal_map, repl_prefix="\\")

mathfrak_map = {}
for c in list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
    mathfrak_map[c] = chr(ord(c)-ord('A')+ord("𝕬"))
font.add_macro_font("mathfrak", mathcal_map, repl_prefix="\\")
font.add_macro_font("frak", mathcal_map, repl_prefix="\\")

font.add_macros({
    "to": "⟶",
    "mapsto": "⟼",
    "uparrow": "↑",
    "downarrow": "↓"
}, repl_prefix="\\")


font.add_ligatures({
    "0": "⁰",
    "1": "¹",
    "2": "²",
    "3": "³",
    "4": "⁴",
    "5": "⁵",
    "6": "⁶",
    "7": "⁷",
    "8": "⁸",
    "9": "⁹"
}, char_prefix="^", fonts=["FiraCode"])
font.add_ligatures({
    "0": "₀",
    "1": "₁",
    "2": "₂",
    "3": "₃",
    "4": "₄",
    "5": "₅",
    "6": "₆",
    "7": "₇",
    "8": "₈",
    "9": "₉"
}, char_prefix="_", fonts=["FiraCode"])

font.add_macro_font("vec",
    {c:c for c in ALPHABETIC},
    repl_prefix="backslash*Default underscore_middle.seq*FiraCode",
    fonts=["DejaVu_Bold"],
    repl_format=("advanced", "unicode", "advanced")
)

undersc_glyph = font.font[font.backend.use_glyph("underscore_middle.seq", fonts=["FiraCode"], format="name")]
undersc_glyph.width = 0

# custom bold greek \balpha, \bbeta, ... (exclude eta since b + eta = beta)
font.add_macros(
    {k: v for k, v in greek_map.items() if not k == "eta"},
    macro_prefix="b",
    repl_prefix="\\b",
    fonts=(None,["DejaVu_Bold"],None)
)

font.save(
    camel_name="Test",
    add_copyright="Programming ligatures added by Ilya Skriblovsky from FiraCode\nFiraCode Copyright (c) 2015 by Nikita Prokopov"
)
