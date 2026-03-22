from copy import deepcopy
from conf import game_constants as gc

INPUT_PANEL_HEIGHT = gc.INPUT_PANEL_HEIGHT
KEYBOARD_PANEL_HEIGHT = gc.KEYBOARD_PANEL_HEIGHT
FLASH_DURATION = 0.18


def _key(label, width, zone):
    return {
        "label": label,
        "width": width,
        "zone": zone,
        "show_label": False,
        "flash": False,
    }


BASE_LAYOUT = [
    [
        _key("`", 1.0, "left"),
        _key("1", 1.0, "left"),
        _key("2", 1.0, "left"),
        _key("3", 1.0, "left"),
        _key("4", 1.0, "left"),
        _key("5", 1.0, "left"),
        _key("6", 1.0, "right"),
        _key("7", 1.0, "right"),
        _key("8", 1.0, "right"),
        _key("9", 1.0, "right"),
        _key("0", 1.0, "right"),
        _key("-", 1.0, "right"),
        _key("=", 1.0, "right"),
        _key("BACK", 2.2, "right"),
    ],
    [
        _key("TAB", 1.7, "left"),
        _key("Q", 1.0, "left"),
        _key("W", 1.0, "left"),
        _key("E", 1.0, "left"),
        _key("R", 1.0, "left"),
        _key("T", 1.0, "left"),
        _key("Y", 1.0, "right"),
        _key("U", 1.0, "right"),
        _key("I", 1.0, "right"),
        _key("O", 1.0, "right"),
        _key("P", 1.0, "right"),
        _key("[", 1.0, "right"),
        _key("]", 1.0, "right"),
        _key("\\", 1.5, "right"),
    ],
    [
        _key("CAPS", 2.0, "left"),
        _key("A", 1.0, "left"),
        _key("S", 1.0, "left"),
        _key("D", 1.0, "left"),
        _key("F", 1.0, "left"),
        _key("G", 1.0, "left"),
        _key("H", 1.0, "right"),
        _key("J", 1.0, "right"),
        _key("K", 1.0, "right"),
        _key("L", 1.0, "right"),
        _key(";", 1.0, "right"),
        _key("'", 1.0, "right"),
        _key("ENTER", 2.3, "right"),
    ],
    [
        _key("SHIFT", 2.5, "left"),
        _key("Z", 1.0, "left"),
        _key("X", 1.0, "left"),
        _key("C", 1.0, "left"),
        _key("V", 1.0, "left"),
        _key("B", 1.0, "left"),
        _key("N", 1.0, "right"),
        _key("M", 1.0, "right"),
        _key(",", 1.0, "right"),
        _key(".", 1.0, "right"),
        _key("/", 1.0, "right"),
        _key("SHIFT", 2.7, "right"),
    ],
    [
        _key("CTRL", 1.5, "left"),
        _key("WIN", 1.2, "left"),
        _key("ALT", 1.2, "left"),
        _key("SPACE", 6.2, "space"),
        _key("ALT", 1.2, "right"),
        _key("FN", 1.2, "right"),
        _key("MENU", 1.2, "right"),
        _key("CTRL", 1.5, "right"),
    ],
]


COMMON_METRICS = {
    "unit_w": gc.KEYBOARD_UNIT_W,
    "key_h": gc.KEYBOARD_KEY_H,
    "gap_x": gc.KEYBOARD_GAP_X,
    "gap_y": gc.KEYBOARD_GAP_Y,
}


COMMON_COLORS = {
    "left": {
        "fill": (55, 120, 80),
        "border": (90, 180, 120),
    },
    "right": {
        "fill": (55, 95, 155),
        "border": (90, 150, 220),
    },
    "space": {
        "fill": (95, 95, 95),
        "border": (150, 150, 150),
    },
    "flash_border": (255, 255, 255),
    "flash_boost": 70,
}


def _is_letter(label):
    return len(label) == 1 and label.isalpha()


def _is_number(label):
    return len(label) == 1 and label.isdigit()


def _is_single_key(label):
    return len(label) == 1


def _build_layout(display_mode):
    layout = deepcopy(BASE_LAYOUT)

    for row in layout:
        for key in row:
            label = key["label"]

            if display_mode == "letters":
                key["show_label"] = _is_letter(label)
                key["flash"] = _is_letter(label)
            elif display_mode == "letters_numbers":
                key["show_label"] = _is_letter(label) or _is_number(label)
                key["flash"] = _is_letter(label) or _is_number(label)
            else:
                key["show_label"] = _is_single_key(label) or label == "SPACE"
                key["flash"] = _is_letter(label) or _is_number(label)

    return layout


KEYBOARD_LEVEL_CONFIGS = {
    "letters": {
        "layout": _build_layout("letters"),
        "metrics": deepcopy(COMMON_METRICS),
        "colors": deepcopy(COMMON_COLORS),
    },
    "letters_numbers": {
        "layout": _build_layout("letters_numbers"),
        "metrics": deepcopy(COMMON_METRICS),
        "colors": deepcopy(COMMON_COLORS),
    },
    "full": {
        "layout": _build_layout("full"),
        "metrics": deepcopy(COMMON_METRICS),
        "colors": deepcopy(COMMON_COLORS),
    },
}


def get_keyboard_config_for_level(level):
    if level <= 1:
        profile = "letters"
    elif level == 2:
        profile = "letters_numbers"
    else:
        profile = "full"

    return deepcopy(KEYBOARD_LEVEL_CONFIGS[profile])
