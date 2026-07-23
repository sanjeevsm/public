"""Central theme / color palette and font-scale for iLab+."""
from typing import Any, Dict

# ── Font scale (used across all screens) ─────────────────────────────────────
F: Dict[str, int] = {
    "brand":  40,   # app logo on home screen
    "h1":     20,   # screen / header titles
    "h2":     16,   # section headings
    "body":   15,   # question text, primary body
    "ui":     14,   # option text, buttons
    "label":  13,   # form labels, secondary UI
    "small":  12,   # captions, hints
    "badge":  11,   # chips, difficulty tags
}

_DARK: Dict[str, Any] = {
    # ── Backgrounds ───────────────────────────────────────────────────────────
    "bg_root":   "#080d14",
    "bg_card":   "#0d1420",
    "bg_option": "#0f1825",
    "bg_header": "#060b12",
    "bg_input":  "#0d1420",
    "bg_alt":    "#0a1018",

    # ── Borders ───────────────────────────────────────────────────────────────
    "border":    "#1e3a5f",
    "border_md": "#243855",

    # ── Interaction ───────────────────────────────────────────────────────────
    "hover":     "#1a2e46",

    # ── Text ─────────────────────────────────────────────────────────────────
    "text":      "#cdd6f4",
    "text_sub":  "#8892b0",
    "text_mute": "#50607a",

    # ── Accent ───────────────────────────────────────────────────────────────
    "accent":    "#4da6ff",
    "acc_hov":   "#3d8fe8",
    "purple":    "#a78bfa",
    "teal":      "#64ffda",
    "amber":     "#ffb347",
    "coral":     "#ff6b6b",
    "gold":      "#ffd700",

    # ── Answer states ─────────────────────────────────────────────────────────
    "ok_bg":     "#0a2a10",
    "ok_fg":     "#00e676",
    "err_bg":    "#2a0808",
    "err_fg":    "#ff5252",

    # ── Bookmark ─────────────────────────────────────────────────────────────
    "bm_on":     "#ffd700",
    "bm_off":    "#404060",

    # ── Category badge palette [(fg, bg) …] ──────────────────────────────────
    "cats": [
        ("#4da6ff", "#081828"), ("#a78bfa", "#120d20"),
        ("#34d399", "#081a12"), ("#fb923c", "#1f1008"),
        ("#f472b6", "#1f0a14"), ("#38bdf8", "#081520"),
        ("#facc15", "#1a1800"), ("#4ade80", "#081a0e"),
    ],

    # ── Option letter colors [(fg, bg) …] ────────────────────────────────────
    "opt_letters": [
        ("#4da6ff", "#08182a"), ("#a78bfa", "#12092a"),
        ("#34d399", "#08180e"), ("#fb923c", "#1a0e04"),
    ],

    "ctk_mode": "dark",
}

_LIGHT: Dict[str, Any] = {
    # ── Backgrounds ───────────────────────────────────────────────────────────
    "bg_root":   "#edf1f7",
    "bg_card":   "#ffffff",
    "bg_option": "#f5f8fc",
    "bg_header": "#d8e2ef",
    "bg_input":  "#f0f4f8",
    "bg_alt":    "#e8edf4",

    # ── Borders ───────────────────────────────────────────────────────────────
    "border":    "#b0c4dc",
    "border_md": "#95b0cc",

    # ── Interaction ───────────────────────────────────────────────────────────
    "hover":     "#dce8f6",

    # ── Text ─────────────────────────────────────────────────────────────────
    "text":      "#1a2a3a",
    "text_sub":  "#4a607a",
    "text_mute": "#7888a0",

    # ── Accent ───────────────────────────────────────────────────────────────
    "accent":    "#1a6ac8",
    "acc_hov":   "#1458a8",
    "purple":    "#6040b0",
    "teal":      "#007a60",
    "amber":     "#a06800",
    "coral":     "#c03030",
    "gold":      "#a08000",

    # ── Answer states ─────────────────────────────────────────────────────────
    "ok_bg":     "#d4f4e4",
    "ok_fg":     "#007840",
    "err_bg":    "#fde4e4",
    "err_fg":    "#c02020",

    # ── Bookmark ─────────────────────────────────────────────────────────────
    "bm_on":     "#a08000",
    "bm_off":    "#8090a8",

    # ── Category badge palette ────────────────────────────────────────────────
    "cats": [
        ("#1a6ac8", "#dce8f8"), ("#6040b0", "#ede0f8"),
        ("#007840", "#d4f4e4"), ("#c04000", "#fce8d8"),
        ("#a02060", "#fce0ec"), ("#0080c0", "#d4eef8"),
        ("#906000", "#fdf0d0"), ("#007030", "#d4f0e0"),
    ],

    # ── Option letter colors ──────────────────────────────────────────────────
    "opt_letters": [
        ("#1a6ac8", "#dce8f8"), ("#6040b0", "#ede0f8"),
        ("#007840", "#d4f4e4"), ("#c04000", "#fce8d8"),
    ],

    "ctk_mode": "light",
}

_mode: str = "dark"


def get() -> Dict[str, Any]:
    return _DARK if _mode == "dark" else _LIGHT


def mode() -> str:
    return _mode


def set_mode(new_mode: str) -> None:
    global _mode
    _mode = new_mode if new_mode in ("dark", "light") else "dark"
    import customtkinter as ctk
    ctk.set_appearance_mode(_mode)


def cat_color(category: str):
    """Return (fg, bg) for a category string — stable across calls."""
    palette = get()["cats"]
    return palette[hash(category) % len(palette)]
