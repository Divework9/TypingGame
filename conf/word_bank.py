"""词库配置。

将英文单词词库与中文拼音词库集中管理，便于后续扩充和维护。
"""

import string

# 单字母模式：26个字母，不分难度
LETTERS = list(string.ascii_lowercase)


def _merge_stage_keys(*groups):
    merged = []
    seen = set()
    for group in groups:
        for key in group:
            if key not in seen:
                merged.append(key)
                seen.add(key)
    return merged


# 单字母模式关卡：
# 1: asdf jkl; gh
# 2: qwertyuiop
# 3: zxcvbnm,.
# 4: 1+2
# 5: 2+3
# 6: 1+3
# 7: 1+2+3
LETTER_STAGE_1_KEYS = list("asdf") + list("jkl") + [";"] + list("gh")
LETTER_STAGE_2_KEYS = list("qwertyuiop")
LETTER_STAGE_3_KEYS = list("zxcvbnm") + [",", "."]

LETTER_STAGE_CONFIGS = [
    {
        "label": "asdf jkl; gh",
        "keys": LETTER_STAGE_1_KEYS,
    },
    {
        "label": "qwertyuiop",
        "keys": LETTER_STAGE_2_KEYS,
    },
    {
        "label": "zxcvbnm,.",
        "keys": LETTER_STAGE_3_KEYS,
    },
    {
        "label": "1+2: asdfghjkl;qwertyuiop",
        "keys": _merge_stage_keys(LETTER_STAGE_1_KEYS, LETTER_STAGE_2_KEYS),
    },
    {
        "label": "2+3: qwertyuiopzxcvbnm,.",
        "keys": _merge_stage_keys(LETTER_STAGE_2_KEYS, LETTER_STAGE_3_KEYS),
    },
    {
        "label": "1+3: asdfghjkl;zxcvbnm,.",
        "keys": _merge_stage_keys(LETTER_STAGE_1_KEYS, LETTER_STAGE_3_KEYS),
    },
    {
        "label": "1+2+3: asdfghjkl;qwertyuiopzxcvbnm,.",
        "keys": _merge_stage_keys(LETTER_STAGE_1_KEYS, LETTER_STAGE_2_KEYS, LETTER_STAGE_3_KEYS),
    },
]

ENGLISH_WORDS = {
    "easy": [
        "cat", "dog", "sun", "red", "big", "run", "hot", "cup",
        "hat", "box", "pen", "map", "bus", "bag", "bed", "fan",
        "fox", "pig", "egg", "ant", "ice", "jam", "key", "leg",
        "van", "web", "quiz", "zoo",
    ],
    "medium": [
        "apple", "happy", "water", "green", "house", "music",
        "tiger", "candy", "cloud", "river", "table", "chair",
        "smile", "sleep", "train", "bread", "light", "plant",
        "stone", "dance", "beach", "dream", "fruit", "paper",
        "jelly", "koala", "queen", "xylophone", "zebra",
    ],
    "hard": [
        "rabbit", "school", "family", "orange", "banana",
        "window", "monkey", "garden", "flower", "bridge",
        "friend", "summer", "winter", "spring", "animal",
        "planet", "rocket", "castle", "forest", "island",
        "jungle", "voyage", "quartz", "xenon", "zipper",
    ],
}


# 中文拼音词库: (汉字显示, 拼音输入)
PINYIN_WORDS = {
    "easy": [
        ("大", "da"), ("小", "xiao"), ("人", "ren"), ("天", "tian"),
        ("水", "shui"), ("火", "huo"), ("山", "shan"), ("月", "yue"),
        ("日", "ri"), ("木", "mu"), ("花", "hua"), ("鸟", "niao"),
        ("鱼", "yu"), ("马", "ma"), ("牛", "niu"), ("羊", "yang"),
        ("猫", "mao"), ("狗", "gou"), ("风", "feng"), ("雨", "yu2"),
        ("包", "bao"), ("草", "cao"), ("家", "jia"), ("口", "kou"),
        ("乐", "le"), ("皮", "pi"), ("去", "qu"), ("王", "wang"),
        ("绿", "lv"), ("字", "zi"),
    ],
    "medium": [
        ("苹果", "pingguo"), ("老师", "laoshi"), ("学校", "xuexiao"),
        ("朋友", "pengyou"), ("快乐", "kuaile"), ("太阳", "taiyang"),
        ("月亮", "yueliang"), ("星星", "xingxing"), ("花朵", "huaduo"),
        ("小鸟", "xiaoniao"), ("大海", "dahai"), ("草地", "caodi"),
        ("蓝天", "lantian"), ("白云", "baiyun"), ("春天", "chuntian"),
        ("秋天", "qiutian"), ("冬天", "dongtian"), ("夏天", "xiatian"),
        ("飞机", "feiji"), ("明月", "mingyue"), ("热水", "reshui"),
        ("外公", "waigong"), ("绿色", "lvse"), ("桌子", "zhuozi"),
    ],
    "hard": [
        ("电脑", "diannao"), ("飞机", "feiji"), ("火车", "huoche"),
        ("图书馆", "tushuguan"), ("动物园", "dongwuyuan"),
        ("巧克力", "qiaokeli"), ("向日葵", "xiangrikui"),
        ("蝴蝶", "hudie"), ("蜻蜓", "qingting"), ("长颈鹿", "changjinglu"),
        ("大象", "daxiang"), ("熊猫", "xiongmao"), ("企鹅", "qie"),
        ("恐龙", "konglong"), ("宇航员", "yuhangyuan"),
        ("宝藏", "baozang"), ("拼图", "pintu"), ("旅行", "lvxing"),
    ],
}
