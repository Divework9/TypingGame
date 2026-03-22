"""Combo 实时评价词配置。"""

import random

# 每 5 个 combo 进入下一鼓励档
COMBO_TIER_STEP = 5
# 鼓励度总档数（达到第 6 档后封顶，不再下降）
COMBO_TIER_COUNT = 6

# 鼓励词配置：从低鼓励度到高鼓励度，每档 3 个候选
COMBO_FEEDBACK_TIERS = [
    ["继续加油", "慢慢变好", "稳步前进"],
    ["有进步哦", "节奏不错", "越打越稳"],
    ["状态在线", "手感起来", "反应真快"],
    ["有点高手", "速度真棒", "连击很稳"],
    ["超强发挥", "太厉害啦", "像小冠军"],
    ["无敌状态", "神速小王", "顶级手感"],
]


def get_feedback_tier_index(combo):
    """根据 combo 获取鼓励档位索引（0-5）。"""
    if combo <= 1:
        return -1
    return min((combo - 1) // COMBO_TIER_STEP, COMBO_TIER_COUNT - 1)


def get_combo_feedback_candidates(combo):
    """返回当前 combo 对应档位的候选词列表。"""
    tier = get_feedback_tier_index(combo)
    if tier < 0:
        return []
    return COMBO_FEEDBACK_TIERS[tier]


def choose_combo_feedback(combo, previous_word="", rng=None):
    """随机选择当前档位词，尽量避免与上一词相同。"""
    candidates = get_combo_feedback_candidates(combo)
    if not candidates:
        return ""

    chooser = rng if rng is not None else random
    pool = [word for word in candidates if word != previous_word]
    if not pool:
        pool = candidates
    return chooser.choice(pool)
