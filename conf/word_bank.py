"""词库配置。

将英文单词词库与中文拼音词库集中管理，便于后续扩充和维护。
"""

ENGLISH_WORDS = {
    "easy": [
        "cat", "dog", "sun", "red", "big", "run", "hot", "cup",
        "hat", "box", "pen", "map", "bus", "bag", "bed", "fan",
        "fox", "pig", "egg", "ant", "ice", "jam", "key", "leg",
    ],
    "medium": [
        "apple", "happy", "water", "green", "house", "music",
        "tiger", "candy", "cloud", "river", "table", "chair",
        "smile", "sleep", "train", "bread", "light", "plant",
        "stone", "dance", "beach", "dream", "fruit", "paper",
    ],
    "hard": [
        "rabbit", "school", "family", "orange", "banana",
        "window", "monkey", "garden", "flower", "bridge",
        "friend", "summer", "winter", "spring", "animal",
        "planet", "rocket", "castle", "forest", "island",
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
    ],
    "medium": [
        ("苹果", "pingguo"), ("老师", "laoshi"), ("学校", "xuexiao"),
        ("朋友", "pengyou"), ("快乐", "kuaile"), ("太阳", "taiyang"),
        ("月亮", "yueliang"), ("星星", "xingxing"), ("花朵", "huaduo"),
        ("小鸟", "xiaoniao"), ("大海", "dahai"), ("草地", "caodi"),
        ("蓝天", "lantian"), ("白云", "baiyun"), ("春天", "chuntian"),
        ("秋天", "qiutian"), ("冬天", "dongtian"), ("夏天", "xiatian"),
    ],
    "hard": [
        ("电脑", "diannao"), ("飞机", "feiji"), ("火车", "huoche"),
        ("图书馆", "tushuguan"), ("动物园", "dongwuyuan"),
        ("巧克力", "qiaokeli"), ("向日葵", "xiangrikui"),
        ("蝴蝶", "hudie"), ("蜻蜓", "qingting"), ("长颈鹿", "changjinglu"),
        ("大象", "daxiang"), ("熊猫", "xiongmao"), ("企鹅", "qie"),
        ("恐龙", "konglong"), ("宇航员", "yuhangyuan"),
    ],
}
