import fontforge

greek = {
    "type": "macro",
    "font": "Latin Modern",
    "macros": {
        "alpha": "α",
        "beta": "β",
        "gamma": "γ",
        "Gamma": "Γ",
        "delta": "δ",
        "Delta": "Δ",
        "varepsilon": "ε",
        "zeta": "ζ",
        "eta": "η",
        "theta": "θ",
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
        "phi": "φ",
        "Phi": "Φ",
        "chi": "χ",
        "psi": "ψ",
        "Psi": "Ψ",
        "omega": "ω",
        "Omega": "Ω",
    }
}

misc = {
    "type": "macro",
    "macros": {
        "infty": "∞",
        "forall": "∀",
        "exists": "∃",
        "nexists": "∄",
        "partial": "∂",
        "emptyset": "∅",
        "cdots": "···",
        "ldots": "…",
    }
}

operators = {
    "type": "macro",
    "macros": {
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
    }
}

mathbb = {
    "type": "macro + char",
    "macros": {
        "mathbb": {
            "N": "ℕ",
            "Z": "ℤ",
            "C": "ℂ",
            "Q": "ℚ"
        }
    }
}

map_arrows = {
    "type": "macro",
    "macros": {
        "to": "⟶",
        "mapsto": "⟼"
    }
}

fonts = {
    "Latin Modern": "latinmodern-math.otf",
    "FiraCode": "FiraCode-Regular.ttf"
}

ligatures = [
    greek,
    operators,
    misc,
    mathbb,
    map_arrows
]