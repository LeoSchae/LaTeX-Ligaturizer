from collections import OrderedDict
from ligaturize import EditFont

font = EditFont(
    font="DroidSansMono.ttf",
    other_fonts=OrderedDict([
        ("DroidSansMono", "DroidSansMono.ttf"),
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
font.add_macros(greek_map, fonts=["DejaVu_Italic"])


font.add_macros({
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

font.add_macros({
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

font.add_macro_font("mathbb", {
        "N": "ℕ",
        "Z": "ℤ",
        "Q": "ℚ",
        "R": "ℝ",
        "C": "ℂ",
    })

font.add_macros({
        "NN": "ℕ",
        "ZZ": "ℤ",
        "QQ": "ℚ",
        "RR": "ℝ",
        "CC": "ℂ"
    })

mathcal_map = {}
for c in list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
    mathcal_map[c] = chr(ord(c)-ord('A')+ord("𝓐"))
font.add_macro_font("mathcal", mathcal_map)
font.add_macro_font("cal", mathcal_map)

mathfrak_map = {}
for c in list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
    mathfrak_map[c] = chr(ord(c)-ord('A')+ord("𝕬"))
font.add_macro_font("mathfrak", mathcal_map)
font.add_macro_font("frak", mathcal_map)

font.add_macros({
    "to": "⟶",
    "mapsto": "⟼"
})


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
}, char_prefix="^")
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
}, char_prefix="_")

# custom bold greek \balpha, \bbeta, ... (exclude eta since b + eta = beta)
font.add_macros(
    {k: v for k, v in greek_map.items() if not k == "eta"},
    macro_prefix="b",
    repl_prefix="b",
    fonts=["DejaVu_Bold"]
)

font.save(
    camel_name="Test",
    add_copyright="Programming ligatures added by Ilya Skriblovsky from FiraCode\nFiraCode Copyright (c) 2015 by Nikita Prokopov"
)