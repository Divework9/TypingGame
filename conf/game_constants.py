"""游戏全局常量配置（非颜色）。

说明：
- 颜色相关常量继续保留在主程序中，不放在这里。
- 与玩法、物理、UI 布局、输入行为相关的数字统一集中管理。
"""

# =============================
# 屏幕与主循环
# =============================
# 窗口宽度（像素）
SCREEN_WIDTH = 800
# 窗口高度（像素）
SCREEN_HEIGHT = 600
# 帧率上限
FPS = 60
# 单帧时间上限（秒），防止跳帧造成逻辑突变
MAX_FRAME_DT = 0.05
# 毫秒转秒的除数
MS_TO_SECONDS = 1000.0

# =============================
# 字体
# =============================
# 大标题字体大小
FONT_SIZE_BIG = 52
# 中号字体大小
FONT_SIZE_MEDIUM = 36
# 小号字体大小
FONT_SIZE_SMALL = 26
# 极小字体大小
FONT_SIZE_TINY = 20
# 输入框字体大小
FONT_SIZE_INPUT = 32

# =============================
# 通用初始状态
# =============================
# 初始分数
INITIAL_SCORE = 0
# 初始生命值
INITIAL_LIVES = 5
# 初始等级
INITIAL_LEVEL = 1
# 初始连击
INITIAL_COMBO = 0
# 初始最高连击
INITIAL_MAX_COMBO = 0
# 初始消除数
INITIAL_WORDS_CLEARED = 0
# 初始漏词数
INITIAL_WORDS_MISSED = 0
# 初始生成计时器
INITIAL_SPAWN_TIMER = 0
# 重开游戏后的生成计时器
RESET_SPAWN_TIMER = 1.0
# 初始游戏时长
INITIAL_GAME_TIME = 0
# 初始震动计时器
INITIAL_SHAKE_TIMER = 0
# 初始闪光计时器
INITIAL_FLASH_TIMER = 0
# 菜单初始选项索引
INITIAL_MENU_SELECTION = 0
# 菜单选项总数
MENU_OPTION_COUNT = 2

# =============================
# 游戏状态枚举值
# =============================
# 菜单态
GAME_STATE_MENU = 0
# 游戏中
GAME_STATE_PLAYING = 1
# 结束态
GAME_STATE_OVER = 2

# =============================
# 难度与计分/升级
# =============================
# easy -> medium 的分数阈值
DIFFICULTY_MEDIUM_SCORE = 100
# medium -> hard 的分数阈值
DIFFICULTY_HARD_SCORE = 300
# 每个字符基础得分
SCORE_PER_CHAR = 10
# 连击加分单位
COMBO_BONUS_UNIT = 5
# 连击加分上限（按连击数封顶）
COMBO_BONUS_CAP = 10
# 每多少分提升一级
LEVEL_SCORE_STEP = 150
# 高评价阈值
COMMENT_HIGH_SCORE = 500
# 中评价阈值
COMMENT_MEDIUM_SCORE = 200

# =============================
# 下落词与生成
# =============================
# 下落词初始 Y 坐标
FALLING_WORD_START_Y = -30
# 触底判定预留边距
FALLING_WORD_OUT_MARGIN = 15
# 拼音行相对汉字的垂直偏移
PINYIN_TEXT_Y_OFFSET = 40
# 生成时左右边距
SPAWN_X_MARGIN = 20
# 生成时可用宽度过小时的最小右边界保护值
SPAWN_X_FALLBACK_MIN = 30
# 防重叠的横向判定阈值
SPAWN_OVERLAP_X_THRESHOLD = 100
# 防重叠的纵向判定阈值
SPAWN_OVERLAP_Y_THRESHOLD = 60

# =============================
# 粒子效果
# =============================
# 粒子水平速度最小值
PARTICLE_VX_MIN = -150
# 粒子水平速度最大值
PARTICLE_VX_MAX = 150
# 粒子垂直速度最小值
PARTICLE_VY_MIN = -200
# 粒子垂直速度最大值
PARTICLE_VY_MAX = -50
# 粒子初始生命周期
PARTICLE_LIFE_INITIAL = 1.0
# 粒子尺寸最小值
PARTICLE_SIZE_MIN = 3
# 粒子尺寸最大值
PARTICLE_SIZE_MAX = 7
# 粒子重力加速度
PARTICLE_GRAVITY = 300
# 粒子生命周期衰减速度
PARTICLE_LIFE_DECAY_RATE = 2
# 粒子最小绘制半径
PARTICLE_DRAW_SIZE_MIN = 1
# 粒子 Alpha 上限
PARTICLE_ALPHA_MAX = 255
# 单次消除生成粒子数量
CLEAR_PARTICLE_COUNT = 15
# 消除粒子 X 随机偏移范围
CLEAR_PARTICLE_X_JITTER = 80
# 消除粒子 Y 固定偏移
CLEAR_PARTICLE_Y_OFFSET = 15

# =============================
# 星星背景
# =============================
# 背景星星数量
STAR_COUNT = 60
# 星星尺寸最小值
STAR_SIZE_MIN = 0.5
# 星星尺寸最大值
STAR_SIZE_MAX = 2
# 星星闪烁速度最小值
STAR_BLINK_SPEED_MIN = 1
# 星星闪烁速度最大值
STAR_BLINK_SPEED_MAX = 3
# 星星相位最大值
STAR_PHASE_MAX = 6.28
# 亮度基准值
STAR_BRIGHTNESS_BASE = 0.4
# 亮度振幅
STAR_BRIGHTNESS_AMPLITUDE = 0.6
# 正弦归一化基准
STAR_SINE_BASE = 0.5
# 正弦归一化振幅
STAR_SINE_AMPLITUDE = 0.5
# 星星蓝色通道比例
STAR_BLUE_RATIO = 0.9
# 星星最小绘制半径
STAR_DRAW_SIZE_MIN = 1

# =============================
# 震动与闪光
# =============================
# 漏词后震动持续时间
MISS_SHAKE_DURATION = 0.3
# 震动随机偏移最小值
SHAKE_OFFSET_MIN = -4
# 震动随机偏移最大值
SHAKE_OFFSET_MAX = 4
# 消除闪光持续时间
CLEAR_FLASH_DURATION = 0.15
# 闪光透明度上限
CLEAR_FLASH_ALPHA_MAX = 40

# =============================
# 顶部信息栏
# =============================
# 顶部信息栏 Y 坐标
TOP_INFO_Y = 8
# 分数文本 X 坐标
SCORE_TEXT_X = 15
# 等级文本 X 坐标
LEVEL_TEXT_X = 200
# 连击文本 X 坐标
COMBO_TEXT_X = 300
# 模式提示距右边偏移
MODE_HINT_RIGHT_OFFSET = 170
# 模式提示额外 Y 偏移
MODE_HINT_Y_OFFSET = 5
# 顶部分隔线 Y 坐标
TOP_DIVIDER_Y = 55

# =============================
# 心形生命值 UI
# =============================
# 心形区域距右边偏移
HEART_PANEL_RIGHT_OFFSET = 170
# 心形区域相对顶部信息栏 Y 偏移
HEART_PANEL_Y_OFFSET = 30
# 心形总数量（与最大生命值一致）
HEART_COUNT = 5
# 相邻心形间距
HEART_GAP = 30
# 心形主体半径
HEART_MAIN_RADIUS = 10
# 心形上方圆的 X 偏移
HEART_LOBE_X_OFFSET = 5
# 心形上方圆的 Y 偏移
HEART_LOBE_Y_OFFSET = 4
# 心形上方圆半径
HEART_LOBE_RADIUS = 6

# =============================
# 菜单布局
# =============================
# 标题 Y 坐标
MENU_TITLE_Y = 120
# 副标题 Y 坐标
MENU_SUBTITLE_Y = 175
# 模式选择标题 Y 坐标
MENU_MODE_TITLE_Y = 260
# 选项起始 Y 坐标
MENU_OPTION_START_Y = 320
# 选项行间距
MENU_OPTION_STEP_Y = 70
# 选中框中心 X 的半宽偏移
MENU_BOX_HALF_WIDTH = 220
# 选中框 Y 偏移
MENU_BOX_Y_OFFSET = 10
# 选中框宽度
MENU_BOX_WIDTH = 440
# 选中框高度
MENU_BOX_HEIGHT = 50
# 选中框圆角
MENU_BOX_RADIUS = 10
# 选项文字 Y 偏移
MENU_OPTION_TEXT_Y_OFFSET = 12
# 底部提示起始 Y 坐标
MENU_HINT_START_Y = 490
# 提示行间距
MENU_HINT_STEP_Y = 28

# =============================
# 输入区域布局
# =============================
# 输入框 X 坐标
INPUT_BOX_X = 20
# 输入框相对输入区域顶部 Y 偏移
INPUT_BOX_Y_OFFSET = 12
# 输入框宽度两侧边距总和
INPUT_BOX_WIDTH_MARGIN = 40
# 输入框高度
INPUT_BOX_HEIGHT = 40
# 输入框圆角
INPUT_BOX_RADIUS = 8
# 输入框边框宽度
INPUT_BOX_BORDER_WIDTH = 2
# 输入文字 X 偏移
INPUT_TEXT_X_OFFSET = 12
# 输入文字 Y 偏移
INPUT_TEXT_Y_OFFSET = 5
# 光标基础 X 偏移
CURSOR_X_BASE_OFFSET = 14
# 光标 Y 偏移
CURSOR_Y_OFFSET = 6
# 光标宽度
CURSOR_WIDTH = 2
# 光标高度
CURSOR_HEIGHT = 28
# 光标闪烁速度系数
CURSOR_BLINK_SPEED = 2
# 光标闪烁取模值
CURSOR_BLINK_MOD = 2
# 键盘区域绘制起点额外 Y 偏移
KEYBOARD_DRAW_Y_OFFSET = 4
# 键盘键帽圆角
KEYBOARD_KEY_RADIUS = 4
# 键盘键帽边框宽度
KEYBOARD_KEY_BORDER_WIDTH = 1

# =============================
# 分隔线与边框
# =============================
# 顶部分隔线宽度
TOP_DIVIDER_WIDTH = 1
# 输入区域上边线宽度
INPUT_AREA_BORDER_WIDTH = 2
# 键盘区域上边线宽度
KEYBOARD_AREA_BORDER_WIDTH = 1

# =============================
# 模式选择索引
# =============================
# 英文模式索引
MENU_SELECTION_ENGLISH = 0
# 拼音模式索引
MENU_SELECTION_PINYIN = 1

# =============================
# 游戏结束页布局
# =============================
# Game Over 标题 Y 坐标
GAME_OVER_TITLE_Y = 100
# 统计信息起始 Y 坐标
GAME_OVER_STATS_START_Y = 200
# 统计信息行间距
GAME_OVER_STATS_STEP_Y = 40
# 评价文本 Y 坐标
GAME_OVER_COMMENT_Y = 430
# 重开提示 Y 坐标
GAME_OVER_HINT_Y = 520

# =============================
# 输入与事件行为
# =============================
# 键盘输入字符截取步长（用于回退一个字符）
INPUT_BACKSPACE_STEP = 1
