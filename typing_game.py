"""
打字练习小游戏 - 适合小学3-6年级
英文单词 + 中文拼音 下落消除模式

依赖: pip install pygame
运行: python typing_game.py


@ name
typing game， 打字游戏
面向初步学打字的 小学生
@ demand 
单词/汉字从屏幕顶部随机下落
玩家在底部输入框打字，匹配成功则消除对应目标，得分
掉到底部未消除则扣一条命
英文模式（单词下落）和拼音模式（汉字下落、打拼音消除）可切换
难度随分数递增（下落加速、单词变长）
适合小学生的大字体、彩色界面

两种模式：英文单词模式（打单词消除）和拼音模式（屏幕显示汉字，打对应拼音消除）。菜单选择，游戏中按 Tab 切换。
动态难度：分数越高，下落越快、单词越长。分三档：easy（短词）→ medium → hard（长词/多字词）。
反馈系统：连击计数（Combo）、消除粒子特效、屏幕震动（漏词时）、生命值心形显示。

输入匹配算法：滑动窗口前缀匹配
- 第1层：检查整个输入是否为词的前缀。若是，返回匹配长度；若否进入第2层。
- 第2-N层：逐步去掉输入的首字符，用剩余部分依次检查是否为词的前缀。
  * 若某个滑动窗口匹配成功，立即返回该位置对应的匹配长度，不继续往后滑。
  * 若全部失败，返回 0（无匹配）。
- 示例：输入"caar"，词"are" → "caar"❌ → "aar"❌ → "ar"✓（作为"are"的前缀） → 返回 2。
- 可视化：打字时已匹配的字母变绿，直观看到进度。拼音模式下汉字在上、拼音在下。

@ 发布流程
一键打包发布脚本：
 .\release\build.ps1 -Clean
 生成的 exe 在 .\release\dist\typing_game.exe 建议整个目录拷贝走
 生成的安装包在 .\release\dist\installer\TypingGame-Setup-0.1.2.exe

import pygame
import random
import sys
import time
from conf.keyboard import (
    INPUT_PANEL_HEIGHT,
    KEYBOARD_PANEL_HEIGHT,
    FLASH_DURATION,
    get_keyboard_config_for_level,
)
from conf.speed import (
    SPAWN_INTERVAL_BASE,
    SPAWN_INTERVAL_SCORE_REDUCTION,
    SPAWN_INTERVAL_MIN,
    FALL_SPEED_BASE,
    FALL_SPEED_SCORE_INCREASE,
    FALL_SPEED_MAX,
    FALL_SPEED_RANDOM_OFFSET,
)
from conf.word_bank import LETTERS, ENGLISH_WORDS, PINYIN_WORDS
from conf.combo_feedback import choose_combo_feedback
from conf import game_constants as gc

# ============================================================
# 初始化
# ============================================================
pygame.init()

SCREEN_W, SCREEN_H = gc.SCREEN_WIDTH, gc.SCREEN_HEIGHT
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("⌨️ 打字大冒险 - Typing Adventure")
clock = pygame.time.Clock()

BOTTOM_UI_HEIGHT = INPUT_PANEL_HEIGHT + KEYBOARD_PANEL_HEIGHT

# ============================================================
# 颜色
# ============================================================
BG_COLOR       = (25, 25, 50)
TEXT_WHITE     = (255, 255, 255)
TEXT_YELLOW    = (255, 220, 80)
TEXT_GREEN     = (80, 230, 120)
TEXT_RED       = (255, 80, 80)
TEXT_CYAN      = (80, 220, 255)
TEXT_ORANGE    = (255, 160, 50)
TEXT_PINK      = (255, 130, 180)
INPUT_BG       = (40, 40, 80)
INPUT_BORDER   = (100, 100, 200)
MATCH_COLOR    = (80, 255, 80)
HEALTH_RED     = (220, 50, 50)
HEALTH_GREEN   = (50, 200, 80)
STAR_COLOR     = (255, 255, 200)

WORD_COLORS = [TEXT_YELLOW, TEXT_CYAN, TEXT_ORANGE, TEXT_PINK, TEXT_GREEN]

# ============================================================
# 字体 (使用系统自带中文字体)
# ============================================================
def get_font(size, bold=False):
    """尝试加载中文字体，失败则用默认字体"""
    font_names = [
        "Microsoft YaHei",    # 微软雅黑
        "SimHei",             # 黑体
        "SimSun",             # 宋体
        "KaiTi",              # 楷体
        "DengXian",           # 等线
        "Source Han Sans CN", # 思源黑体
    ]
    for name in font_names:
        try:
            f = pygame.font.SysFont(name, size, bold=bold)
            # 测试能否渲染中文
            f.render("测试", True, TEXT_WHITE)
            return f
        except:
            continue
    return pygame.font.Font(None, size)

font_big    = get_font(gc.FONT_SIZE_BIG, bold=True)
font_medium = get_font(gc.FONT_SIZE_MEDIUM, bold=True)
font_small  = get_font(gc.FONT_SIZE_SMALL)
font_combo  = get_font(gc.FONT_SIZE_COMBO)
font_tiny   = get_font(gc.FONT_SIZE_TINY)
font_input  = get_font(gc.FONT_SIZE_INPUT, bold=True)

# ============================================================
# 游戏对象
# ============================================================
class FallingWord:
    def __init__(self, display_text, type_text, x, speed, color):
        self.display_text = display_text   # 屏幕上显示的文字
        self.type_text = type_text         # 需要输入的内容
        self.x = x
        self.y = gc.FALLING_WORD_START_Y
        self.speed = speed
        self.color = color
        self.matched_chars = gc.INITIAL_COMBO  # 已匹配的字符数
        self.active = True

    def update(self, dt):
        self.y += self.speed * dt

    def is_out(self):
        return self.y > SCREEN_H - (BOTTOM_UI_HEIGHT + gc.FALLING_WORD_OUT_MARGIN)

    def draw(self, surface):
        # 画已匹配部分（绿色）和未匹配部分（原色）
        typed = self.type_text[:self.matched_chars]
        remaining = self.type_text[self.matched_chars:]

        # 如果是拼音模式，显示汉字在上，拼音在下
        if self.display_text != self.type_text:
            # 汉字
            hanzi_surf = font_medium.render(self.display_text, True, self.color)
            surface.blit(hanzi_surf, (self.x, self.y))
            # 拼音（已输入部分绿色 + 未输入部分白色）
            pinyin_y = self.y + gc.PINYIN_TEXT_Y_OFFSET
            if typed:
                typed_surf = font_small.render(typed, True, MATCH_COLOR)
                surface.blit(typed_surf, (self.x, pinyin_y))
                offset = typed_surf.get_width()
            else:
                offset = gc.INITIAL_COMBO
            if remaining:
                remain_surf = font_small.render(remaining, True, TEXT_WHITE)
                surface.blit(remain_surf, (self.x + offset, pinyin_y))
        else:
            # 英文模式：已输入绿色 + 未输入原色
            if typed:
                typed_surf = font_medium.render(typed, True, MATCH_COLOR)
                surface.blit(typed_surf, (self.x, self.y))
                offset = typed_surf.get_width()
            else:
                offset = gc.INITIAL_COMBO
            if remaining:
                remain_surf = font_medium.render(remaining, True, self.color)
                surface.blit(remain_surf, (self.x + offset, self.y))


class Particle:
    """消除特效粒子"""
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(gc.PARTICLE_VX_MIN, gc.PARTICLE_VX_MAX)
        self.vy = random.uniform(gc.PARTICLE_VY_MIN, gc.PARTICLE_VY_MAX)
        self.life = gc.PARTICLE_LIFE_INITIAL
        self.color = color
        self.size = random.randint(gc.PARTICLE_SIZE_MIN, gc.PARTICLE_SIZE_MAX)

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += gc.PARTICLE_GRAVITY * dt  # 重力
        self.life -= dt * gc.PARTICLE_LIFE_DECAY_RATE
        return self.life > gc.INITIAL_COMBO

    def draw(self, surface):
        alpha = max(gc.INITIAL_COMBO, int(self.life * gc.PARTICLE_ALPHA_MAX))
        r, g, b = self.color
        s = max(gc.PARTICLE_DRAW_SIZE_MIN, int(self.size * self.life))
        pygame.draw.circle(surface, (r, g, b), (int(self.x), int(self.y)), s)


class Star:
    """背景星星"""
    def __init__(self):
        self.x = random.randint(gc.GAME_STATE_MENU, SCREEN_W)
        self.y = random.randint(gc.GAME_STATE_MENU, SCREEN_H)
        self.size = random.uniform(gc.STAR_SIZE_MIN, gc.STAR_SIZE_MAX)
        self.blink_speed = random.uniform(gc.STAR_BLINK_SPEED_MIN, gc.STAR_BLINK_SPEED_MAX)
        self.phase = random.uniform(gc.GAME_STATE_MENU, gc.STAR_PHASE_MAX)

    def draw(self, surface, t):
        import math
        brightness = gc.STAR_BRIGHTNESS_BASE + gc.STAR_BRIGHTNESS_AMPLITUDE * (
            gc.STAR_SINE_BASE + gc.STAR_SINE_AMPLITUDE * math.sin(t * self.blink_speed + self.phase)
        )
        c = int(gc.PARTICLE_ALPHA_MAX * brightness)
        color = (c, c, int(c * gc.STAR_BLUE_RATIO))
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), max(gc.STAR_DRAW_SIZE_MIN, int(self.size)))


# ============================================================
# 游戏主类
# ============================================================
class TypingGame:
    # 游戏状态
    STATE_MENU = gc.GAME_STATE_MENU
    STATE_PLAYING = gc.GAME_STATE_PLAYING
    STATE_OVER = gc.GAME_STATE_OVER

    def __init__(self):
        self.state = self.STATE_MENU
        self.mode = "letter"          # "letter", "english" 或 "pinyin"
        self.score = gc.INITIAL_SCORE
        self.lives = gc.INITIAL_LIVES
        self.level = gc.INITIAL_LEVEL
        self.words = []               # 当前屏幕上的下落词
        self.particles = []
        self.input_text = ""
        self.combo = gc.INITIAL_COMBO
        self.combo_feedback_word = ""
        self.max_combo = gc.INITIAL_MAX_COMBO
        self.words_cleared = gc.INITIAL_WORDS_CLEARED
        self.words_missed = gc.INITIAL_WORDS_MISSED
        self.spawn_timer = gc.INITIAL_SPAWN_TIMER
        self.game_time = gc.INITIAL_GAME_TIME
        self.stars = [Star() for _ in range(gc.STAR_COUNT)]
        self.shake_timer = gc.INITIAL_SHAKE_TIMER  # 屏幕震动
        self.flash_timer = gc.INITIAL_FLASH_TIMER  # 消除闪光
        self.keyboard_layout = []
        self.keyboard_colors = {}
        self.keyboard_metrics = {}
        self.key_flash = {}
        self.apply_keyboard_config()

        # 菜单选项
        self.menu_selection = gc.INITIAL_MENU_SELECTION

    def apply_keyboard_config(self):
        keyboard_config = get_keyboard_config_for_level(self.level)
        self.keyboard_layout = keyboard_config["layout"]
        self.keyboard_colors = keyboard_config["colors"]
        self.keyboard_metrics = keyboard_config["metrics"]

        old_flash = self.key_flash
        self.key_flash = {}
        for row in self.keyboard_layout:
            for key in row:
                if key.get("flash", False):
                    flash_key = key["label"].lower()
                    self.key_flash[flash_key] = old_flash.get(flash_key, gc.INITIAL_FLASH_TIMER)

    def trigger_key_flash(self, letter):
        key = letter.lower()
        if key in self.key_flash:
            self.key_flash[key] = FLASH_DURATION

    def update_key_flash(self, dt):
        for key in self.key_flash:
            self.key_flash[key] = max(gc.INITIAL_FLASH_TIMER, self.key_flash[key] - dt)

    def get_difficulty(self):
        if self.score < gc.DIFFICULTY_MEDIUM_SCORE:
            return "easy"
        elif self.score < gc.DIFFICULTY_HARD_SCORE:
            return "medium"
        else:
            return "hard"

    def get_spawn_interval(self):
        """根据分数动态调整生成间隔"""
        reduction = self.score * SPAWN_INTERVAL_SCORE_REDUCTION
        return max(SPAWN_INTERVAL_MIN, SPAWN_INTERVAL_BASE - reduction)

    def get_fall_speed(self):
        """根据分数动态调整下落速度"""
        increase = self.score * FALL_SPEED_SCORE_INCREASE
        return min(FALL_SPEED_MAX, FALL_SPEED_BASE + increase)

    def spawn_word(self):
        diff = self.get_difficulty()
        speed = self.get_fall_speed() + random.uniform(-FALL_SPEED_RANDOM_OFFSET, FALL_SPEED_RANDOM_OFFSET)
        color = random.choice(WORD_COLORS)

        if self.mode == "letter":
            letter = random.choice(LETTERS)
            display = letter
            type_text = letter
        elif self.mode == "english":
            word = random.choice(ENGLISH_WORDS[diff])
            display = word
            type_text = word
        else:
            hanzi, pinyin = random.choice(PINYIN_WORDS[diff])
            display = hanzi
            # 去掉拼音中的数字标记(如 yu2 -> yu)
            type_text = ''.join(c for c in pinyin if not c.isdigit())

        # 计算文字宽度防止超出屏幕
        test_surf = font_medium.render(display, True, TEXT_WHITE)
        max_x = SCREEN_W - test_surf.get_width() - gc.SPAWN_X_MARGIN
        x = random.randint(gc.SPAWN_X_MARGIN, max(gc.SPAWN_X_FALLBACK_MIN, max_x))

        # 避免和已有词重叠
        for existing in self.words:
            if abs(existing.x - x) < gc.SPAWN_OVERLAP_X_THRESHOLD and existing.y < gc.SPAWN_OVERLAP_Y_THRESHOLD:
                x = random.randint(gc.SPAWN_X_MARGIN, max(gc.SPAWN_X_FALLBACK_MIN, max_x))
                break

        self.words.append(FallingWord(display, type_text, x, speed, color))

    def check_input(self):
        """检查当前输入是否匹配任何下落词 - 使用滑动窗口前缀匹配"""
        if not self.input_text:
            for w in self.words:
                w.matched_chars = gc.INITIAL_COMBO
            return

        input_lower = self.input_text.lower()
        exact_match_candidates = []

        for index, w in enumerate(self.words):
            if not w.active:
                w.matched_chars = gc.INITIAL_COMBO
                continue

            matched = gc.INITIAL_COMBO
            for start_pos in range(len(input_lower)):
                substring = input_lower[start_pos:]
                if w.type_text.startswith(substring):
                    matched = len(substring)
                    if substring == w.type_text:
                        exact_match_candidates.append({"y": w.y, "index": index, "word": w})
                    break

            w.matched_chars = matched

        if exact_match_candidates:
            # 同词同时命中时，优先消除更靠近底部（y更大）的目标；同y时按原列表顺序稳定处理
            target = max(exact_match_candidates, key=lambda item: (item["y"], -item["index"]))["word"]
            self.clear_word(target)
            self.input_text = ""
            # 清除后剩余词不应保留旧高亮状态
            for w in self.words:
                if w.active:
                    w.matched_chars = gc.INITIAL_COMBO

    def clear_word(self, word):
        """消除一个词"""
        word.active = False

        # 计分
        base_score = len(word.type_text) * gc.SCORE_PER_CHAR
        self.combo += gc.GAME_STATE_PLAYING
        self.combo_feedback_word = choose_combo_feedback(self.combo, self.combo_feedback_word)
        combo_bonus = min(self.combo, gc.COMBO_BONUS_CAP) * gc.COMBO_BONUS_UNIT
        self.score += base_score + combo_bonus
        self.words_cleared += gc.GAME_STATE_PLAYING
        self.max_combo = max(self.max_combo, self.combo)

        # 升级检测
        new_level = gc.INITIAL_LEVEL + self.score // gc.LEVEL_SCORE_STEP
        if new_level > self.level:
            self.level = new_level
            self.apply_keyboard_config()

        # 特效
        self.flash_timer = gc.CLEAR_FLASH_DURATION
        for _ in range(gc.CLEAR_PARTICLE_COUNT):
            self.particles.append(Particle(
                word.x + random.randint(gc.GAME_STATE_MENU, gc.CLEAR_PARTICLE_X_JITTER),
                word.y + gc.CLEAR_PARTICLE_Y_OFFSET,
                word.color
            ))

    def miss_word(self, word):
        """漏掉一个词"""
        word.active = False
        self.lives -= gc.GAME_STATE_PLAYING
        self.combo = gc.INITIAL_COMBO
        self.combo_feedback_word = ""
        self.words_missed += gc.GAME_STATE_PLAYING
        self.shake_timer = gc.MISS_SHAKE_DURATION

        if self.lives <= gc.GAME_STATE_MENU:
            self.state = self.STATE_OVER

    def update(self, dt):
        if self.state != self.STATE_PLAYING:
            return

        self.game_time += dt
        self.shake_timer = max(gc.INITIAL_SHAKE_TIMER, self.shake_timer - dt)
        self.flash_timer = max(gc.INITIAL_FLASH_TIMER, self.flash_timer - dt)
        self.update_key_flash(dt)

        # 生成新词
        self.spawn_timer -= dt
        if self.spawn_timer <= gc.GAME_STATE_MENU:
            self.spawn_word()
            self.spawn_timer = self.get_spawn_interval()

        # 更新下落词
        for w in self.words:
            if w.active:
                w.update(dt)
                if w.is_out():
                    self.miss_word(w)

        # 清理无效词
        self.words = [w for w in self.words if w.active]

        # 更新粒子
        self.particles = [p for p in self.particles if p.update(dt)]

    def draw_menu(self):
        screen.fill(BG_COLOR)

        # 背景星星
        t = time.time()
        for star in self.stars:
            star.draw(screen, t)

        # 标题
        title = font_big.render("打字大冒险", True, TEXT_YELLOW)
        title_rect = title.get_rect(center=(SCREEN_W // gc.MENU_OPTION_COUNT, gc.MENU_TITLE_Y))
        screen.blit(title, title_rect)

        subtitle = font_small.render("Typing Adventure", True, TEXT_CYAN)
        sub_rect = subtitle.get_rect(center=(SCREEN_W // gc.MENU_OPTION_COUNT, gc.MENU_SUBTITLE_Y))
        screen.blit(subtitle, sub_rect)

        # 模式选择
        mode_title = font_small.render("选择模式 / Select Mode:", True, TEXT_WHITE)
        screen.blit(mode_title, mode_title.get_rect(center=(SCREEN_W // gc.MENU_OPTION_COUNT, gc.MENU_MODE_TITLE_Y)))

        options = [
            ("🔤  单字母模式  Single Letters", "letter"),
            ("📖  英文单词模式  English Words", "english"),
            ("📝  中文拼音模式  Chinese Pinyin", "pinyin"),
        ]

        for i, (text, mode) in enumerate(options):
            y = gc.MENU_OPTION_START_Y + i * gc.MENU_OPTION_STEP_Y
            is_selected = (i == self.menu_selection)

            if is_selected:
                # 选中框
                box_rect = pygame.Rect(
                    SCREEN_W // gc.MENU_OPTION_COUNT - gc.MENU_BOX_HALF_WIDTH,
                    y - gc.MENU_BOX_Y_OFFSET,
                    gc.MENU_BOX_WIDTH,
                    gc.MENU_BOX_HEIGHT,
                )
                pygame.draw.rect(screen, (60, 60, 120), box_rect, border_radius=gc.MENU_BOX_RADIUS)
                pygame.draw.rect(screen, TEXT_CYAN, box_rect, gc.MENU_OPTION_COUNT, border_radius=gc.MENU_BOX_RADIUS)
                color = TEXT_YELLOW
            else:
                color = (150, 150, 180)

            opt_surf = font_small.render(text, True, color)
            opt_rect = opt_surf.get_rect(center=(SCREEN_W // gc.MENU_OPTION_COUNT, y + gc.MENU_OPTION_TEXT_Y_OFFSET))
            screen.blit(opt_surf, opt_rect)

        # 操作提示
        hints = [
            "↑↓ 选择模式    Enter 开始游戏",
            "打字消除下落的单词，别让它们落到底部！",
        ]
        for i, hint in enumerate(hints):
            h_surf = font_tiny.render(hint, True, (120, 120, 160))
            h_rect = h_surf.get_rect(center=(SCREEN_W // gc.MENU_OPTION_COUNT, gc.MENU_HINT_START_Y + i * gc.MENU_HINT_STEP_Y))
            screen.blit(h_surf, h_rect)

    def draw_game(self):
        # 屏幕震动偏移
        import math
        if self.shake_timer > gc.GAME_STATE_MENU:
            ox = random.randint(gc.SHAKE_OFFSET_MIN, gc.SHAKE_OFFSET_MAX)
            oy = random.randint(gc.SHAKE_OFFSET_MIN, gc.SHAKE_OFFSET_MAX)
        else:
            ox, oy = gc.GAME_STATE_MENU, gc.GAME_STATE_MENU

        screen.fill(BG_COLOR)

        # 背景星星
        t = time.time()
        for star in self.stars:
            star.draw(screen, t)

        # 闪光效果
        if self.flash_timer > gc.GAME_STATE_MENU:
            flash_alpha = int(self.flash_timer / gc.CLEAR_FLASH_DURATION * gc.CLEAR_FLASH_ALPHA_MAX)
            flash_surf = pygame.Surface((SCREEN_W, SCREEN_H))
            flash_surf.fill(TEXT_WHITE)
            flash_surf.set_alpha(flash_alpha)
            screen.blit(flash_surf, (gc.GAME_STATE_MENU, gc.GAME_STATE_MENU))

        # 顶部信息栏
        info_y = gc.TOP_INFO_Y
        # 分数
        score_text = font_small.render(f"分数: {self.score}", True, TEXT_YELLOW)
        screen.blit(score_text, (gc.SCORE_TEXT_X + ox, info_y + oy))

        # 等级
        level_text = font_small.render(f"Lv.{self.level}", True, TEXT_CYAN)
        screen.blit(level_text, (gc.LEVEL_TEXT_X + ox, info_y + oy))

        # Combo
        if self.combo > gc.GAME_STATE_PLAYING:
            anchor_bottom = info_y + oy + level_text.get_height()
            level_right = gc.LEVEL_TEXT_X + ox + level_text.get_width()

            feedback = self.combo_feedback_word
            feedback_width = gc.GAME_STATE_MENU
            feedback_text = None
            if feedback:
                feedback_text = font_small.render(feedback, True, TEXT_GREEN)

                feedback_width = feedback_text.get_width()

            # 根据 Lv 右边界和反馈词宽度，动态计算 Combo 左边界，避免重叠
            combo_x = max(
                gc.COMBO_TEXT_X + ox,
                level_right + gc.COMBO_FEEDBACK_GAP + feedback_width + gc.COMBO_FEEDBACK_GAP,
            )

            if feedback_text:
                feedback_x = combo_x - gc.COMBO_FEEDBACK_GAP - feedback_width
                feedback_y = anchor_bottom - feedback_text.get_height()
                screen.blit(feedback_text, (feedback_x, feedback_y))

            combo_text = font_combo.render(f"Combo x{self.combo}!", True, TEXT_ORANGE)
            combo_y = anchor_bottom - combo_text.get_height()
            screen.blit(combo_text, (combo_x, combo_y))

        # 模式
        mode_labels = {"letter": "字母", "english": "英文", "pinyin": "拼音"}
        mode_label = mode_labels.get(self.mode, "英文")
        mode_text = font_tiny.render(f"[{mode_label}] Tab切换", True, (120, 120, 160))
        screen.blit(mode_text, (SCREEN_W - gc.MODE_HINT_RIGHT_OFFSET + ox, info_y + gc.MODE_HINT_Y_OFFSET + oy))

        # 生命值
        heart_x = SCREEN_W - gc.HEART_PANEL_RIGHT_OFFSET
        heart_y = info_y + gc.HEART_PANEL_Y_OFFSET
        for i in range(gc.HEART_COUNT):
            color = HEALTH_RED if i < self.lives else (60, 60, 60)

            center_x = heart_x + i * gc.HEART_GAP + ox
            center_y = heart_y + oy
            left_lobe_x = center_x - gc.HEART_LOBE_X_OFFSET
            right_lobe_x = center_x + gc.HEART_LOBE_X_OFFSET
            lobe_y = center_y - gc.HEART_LOBE_Y_OFFSET
            bottom_y = center_y + gc.HEART_MAIN_RADIUS + gc.HEART_LOBE_RADIUS

            # 缩放自适应心形：两个上半圆 + 下三角
            pygame.draw.circle(
                screen,
                color,
                (left_lobe_x, lobe_y),
                gc.HEART_LOBE_RADIUS,
            )
            pygame.draw.circle(
                screen,
                color,
                (right_lobe_x, lobe_y),
                gc.HEART_LOBE_RADIUS,
            )
            pygame.draw.polygon(
                screen,
                color,
                [
                    (left_lobe_x - gc.HEART_LOBE_RADIUS, lobe_y),
                    (right_lobe_x + gc.HEART_LOBE_RADIUS, lobe_y),
                    (center_x, bottom_y),
                ],
            )

        # 分隔线
        pygame.draw.line(
            screen,
            (60, 60, 100),
            (gc.GAME_STATE_MENU, gc.TOP_DIVIDER_Y),
            (SCREEN_W, gc.TOP_DIVIDER_Y),
            gc.TOP_DIVIDER_WIDTH,
        )

        # 下落词
        for w in self.words:
            w.draw(screen)

        # 粒子
        for p in self.particles:
            p.draw(screen)

        # 底部输入区域（上）
        input_area_y = SCREEN_H - BOTTOM_UI_HEIGHT
        pygame.draw.rect(screen, INPUT_BG, (gc.GAME_STATE_MENU, input_area_y, SCREEN_W, INPUT_PANEL_HEIGHT))
        pygame.draw.line(
            screen,
            INPUT_BORDER,
            (gc.GAME_STATE_MENU, input_area_y),
            (SCREEN_W, input_area_y),
            gc.INPUT_AREA_BORDER_WIDTH,
        )

        # 输入框
        box_x, box_y = gc.INPUT_BOX_X, input_area_y + gc.INPUT_BOX_Y_OFFSET
        box_w, box_h = SCREEN_W - gc.INPUT_BOX_WIDTH_MARGIN, gc.INPUT_BOX_HEIGHT
        pygame.draw.rect(screen, (30, 30, 65), (box_x, box_y, box_w, box_h), border_radius=gc.INPUT_BOX_RADIUS)
        pygame.draw.rect(
            screen,
            INPUT_BORDER,
            (box_x, box_y, box_w, box_h),
            gc.INPUT_BOX_BORDER_WIDTH,
            border_radius=gc.INPUT_BOX_RADIUS,
        )

        # 输入文字
        if self.input_text:
            input_surf = font_input.render(self.input_text, True, TEXT_WHITE)
        else:
            placeholders = {
                "letter": "按下字母键消除它们...",
                "english": "输入单词消除它们...",
                "pinyin": "输入拼音消除汉字...",
            }
            placeholder = placeholders.get(self.mode, "输入单词消除它们...")
            input_surf = font_input.render(placeholder, True, (80, 80, 120))
        screen.blit(input_surf, (box_x + gc.INPUT_TEXT_X_OFFSET, box_y + gc.INPUT_TEXT_Y_OFFSET))

        # 光标闪烁
        if self.input_text or int(time.time() * gc.CURSOR_BLINK_SPEED) % gc.CURSOR_BLINK_MOD:
            cursor_rect = self._compute_input_cursor_rect(box_x, box_y, box_h)
            pygame.draw.rect(screen, TEXT_WHITE, cursor_rect)

        # 底部键盘区域（下）
        keyboard_area_y = input_area_y + INPUT_PANEL_HEIGHT
        pygame.draw.rect(
            screen,
            (30, 30, 70),
            (gc.GAME_STATE_MENU, keyboard_area_y, SCREEN_W, KEYBOARD_PANEL_HEIGHT),
        )
        pygame.draw.line(
            screen,
            INPUT_BORDER,
            (gc.GAME_STATE_MENU, keyboard_area_y),
            (SCREEN_W, keyboard_area_y),
            gc.KEYBOARD_AREA_BORDER_WIDTH,
        )
        self.draw_keyboard(keyboard_area_y + gc.KEYBOARD_DRAW_Y_OFFSET, ox, oy)

    def _compute_input_cursor_rect(self, box_x, box_y, box_h):
        """计算输入光标位置：在缩放下与输入文字保持底部对齐。"""
        text_top = box_y + gc.INPUT_TEXT_Y_OFFSET
        typed_width = font_input.size(self.input_text)[0]
        cursor_x = box_x + gc.CURSOR_X_BASE_OFFSET + typed_width

        # 以输入字体渲染高度为基准，统一做底部对齐
        text_h = font_input.get_height()
        cursor_h = max(gc.GAME_STATE_PLAYING, min(gc.CURSOR_HEIGHT, text_h))
        text_bottom = text_top + text_h
        cursor_y = text_bottom - cursor_h

        # 钳制到输入框可视区域
        top_bound = box_y + gc.INPUT_BOX_BORDER_WIDTH
        bottom_bound = box_y + box_h - gc.INPUT_BOX_BORDER_WIDTH
        cursor_y = max(top_bound, min(int(cursor_y), bottom_bound - gc.GAME_STATE_PLAYING))
        cursor_h = max(gc.GAME_STATE_PLAYING, min(int(cursor_h), bottom_bound - cursor_y))

        return pygame.Rect(int(cursor_x), int(cursor_y), gc.CURSOR_WIDTH, cursor_h)

    def draw_keyboard(self, start_y, ox=gc.GAME_STATE_MENU, oy=gc.GAME_STATE_MENU):
        unit_w = self.keyboard_metrics["unit_w"]
        key_h = self.keyboard_metrics["key_h"]
        gap_x = self.keyboard_metrics["gap_x"]
        gap_y = self.keyboard_metrics["gap_y"]

        for row_index, row in enumerate(self.keyboard_layout):
            row_width = sum(int(unit_w * key["width"]) for key in row) + gap_x * (len(row) - gc.GAME_STATE_PLAYING)
            start_x = (SCREEN_W - row_width) // gc.MENU_OPTION_COUNT
            y = start_y + row_index * (key_h + gap_y)

            x = start_x
            for key in row:
                label = key["label"]
                zone = key["zone"]
                key_w = int(unit_w * key["width"])

                zone_color = self.keyboard_colors[zone]
                base_fill = zone_color["fill"]
                base_border = zone_color["border"]

                flash_key = label.lower()
                is_flashing = flash_key in self.key_flash and self.key_flash[flash_key] > gc.GAME_STATE_MENU
                if is_flashing:
                    flash_boost = self.keyboard_colors["flash_boost"]
                    fill_color = (
                        min(gc.PARTICLE_ALPHA_MAX, base_fill[gc.GAME_STATE_MENU] + flash_boost),
                        min(gc.PARTICLE_ALPHA_MAX, base_fill[gc.GAME_STATE_PLAYING] + flash_boost),
                        min(gc.PARTICLE_ALPHA_MAX, base_fill[gc.GAME_STATE_OVER] + flash_boost),
                    )
                    border_color = self.keyboard_colors["flash_border"]
                else:
                    fill_color = base_fill
                    border_color = base_border

                rect = pygame.Rect(x + ox, y + oy, key_w, key_h)
                pygame.draw.rect(screen, fill_color, rect, border_radius=gc.KEYBOARD_KEY_RADIUS)
                pygame.draw.rect(screen, border_color, rect, gc.KEYBOARD_KEY_BORDER_WIDTH, border_radius=gc.KEYBOARD_KEY_RADIUS)

                if key.get("show_label", False):
                    txt = font_tiny.render(label.upper(), True, TEXT_WHITE)
                    txt_rect = txt.get_rect(center=rect.center)
                    screen.blit(txt, txt_rect)

                x += key_w + gap_x

    def draw_game_over(self):
        screen.fill(BG_COLOR)

        t = time.time()
        for star in self.stars:
            star.draw(screen, t)

        # Game Over 标题
        title = font_big.render("游戏结束!", True, TEXT_RED)
        title_rect = title.get_rect(center=(SCREEN_W // gc.MENU_OPTION_COUNT, gc.GAME_OVER_TITLE_Y))
        screen.blit(title, title_rect)

        # 统计信息
        stats = [
            f"最终得分: {self.score}",
            f"消除单词: {self.words_cleared}",
            f"最高连击: {self.max_combo}",
            f"最终等级: Lv.{self.level}",
            f"游戏时长: {int(self.game_time)}秒",
        ]

        for i, stat in enumerate(stats):
            color = TEXT_YELLOW if i == gc.GAME_STATE_MENU else TEXT_WHITE
            s = font_small.render(stat, True, color)
            r = s.get_rect(center=(SCREEN_W // gc.MENU_OPTION_COUNT, gc.GAME_OVER_STATS_START_Y + i * gc.GAME_OVER_STATS_STEP_Y))
            screen.blit(s, r)

        # 评价
        if self.score >= gc.COMMENT_HIGH_SCORE:
            comment = "太厉害了！打字高手！🌟"
            c_color = TEXT_YELLOW
        elif self.score >= gc.COMMENT_MEDIUM_SCORE:
            comment = "不错哦！继续加油！💪"
            c_color = TEXT_GREEN
        else:
            comment = "多练习就会越来越好！📖"
            c_color = TEXT_CYAN

        comment_surf = font_medium.render(comment, True, c_color)
        comment_rect = comment_surf.get_rect(center=(SCREEN_W // gc.MENU_OPTION_COUNT, gc.GAME_OVER_COMMENT_Y))
        screen.blit(comment_surf, comment_rect)

        # 提示
        hint = font_small.render("按 Enter 重新开始    按 Esc 返回菜单", True, (120, 120, 160))
        hint_rect = hint.get_rect(center=(SCREEN_W // gc.MENU_OPTION_COUNT, gc.GAME_OVER_HINT_Y))
        screen.blit(hint, hint_rect)

    def reset_game(self):
        self.score = gc.INITIAL_SCORE
        self.lives = gc.INITIAL_LIVES
        self.level = gc.INITIAL_LEVEL
        self.words = []
        self.particles = []
        self.input_text = ""
        self.combo = gc.INITIAL_COMBO
        self.combo_feedback_word = ""
        self.max_combo = gc.INITIAL_MAX_COMBO
        self.words_cleared = gc.INITIAL_WORDS_CLEARED
        self.words_missed = gc.INITIAL_WORDS_MISSED
        self.spawn_timer = gc.RESET_SPAWN_TIMER
        self.game_time = gc.INITIAL_GAME_TIME
        self.shake_timer = gc.INITIAL_SHAKE_TIMER
        self.flash_timer = gc.INITIAL_FLASH_TIMER
        self.apply_keyboard_config()
        for key in self.key_flash:
            self.key_flash[key] = gc.INITIAL_FLASH_TIMER

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            return False

        if event.type == pygame.KEYDOWN:
            if self.state == self.STATE_MENU:
                if event.key == pygame.K_UP:
                    self.menu_selection = (self.menu_selection - gc.GAME_STATE_PLAYING) % gc.MENU_OPTION_COUNT
                elif event.key == pygame.K_DOWN:
                    self.menu_selection = (self.menu_selection + gc.GAME_STATE_PLAYING) % gc.MENU_OPTION_COUNT
                elif event.key == pygame.K_RETURN:
                    if self.menu_selection == gc.MENU_SELECTION_LETTER:
                        self.mode = "letter"
                    elif self.menu_selection == gc.MENU_SELECTION_ENGLISH:
                        self.mode = "english"
                    else:
                        self.mode = "pinyin"
                    self.reset_game()
                    self.state = self.STATE_PLAYING

            elif self.state == self.STATE_PLAYING:
                if event.unicode and event.unicode.lower() in self.key_flash:
                    self.trigger_key_flash(event.unicode)

                if event.key == pygame.K_ESCAPE:
                    self.state = self.STATE_MENU
                elif event.key == pygame.K_TAB:
                    # 切换模式
                    mode_cycle = ["letter", "english", "pinyin"]
                    idx = mode_cycle.index(self.mode) if self.mode in mode_cycle else 0
                    self.mode = mode_cycle[(idx + 1) % len(mode_cycle)]
                    self.input_text = ""
                    for w in self.words:
                        w.matched_chars = gc.INITIAL_COMBO
                elif event.key == pygame.K_BACKSPACE:
                    self.input_text = self.input_text[:-gc.INPUT_BACKSPACE_STEP]
                    self.check_input()
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    # 回车/空格清空输入（不匹配时重来）
                    self.input_text = ""
                    for w in self.words:
                        w.matched_chars = gc.INITIAL_COMBO
                elif event.unicode and event.unicode.isalpha():
                    typed_key = event.unicode.lower()
                    self.input_text += typed_key
                    self.check_input()

            elif self.state == self.STATE_OVER:
                if event.key == pygame.K_RETURN:
                    self.reset_game()
                    self.state = self.STATE_PLAYING
                elif event.key == pygame.K_ESCAPE:
                    self.state = self.STATE_MENU

        return True

    def run(self):
        running = True
        while running:
            dt = clock.tick(gc.FPS) / gc.MS_TO_SECONDS
            dt = min(dt, gc.MAX_FRAME_DT)  # 防止跳帧

            for event in pygame.event.get():
                if not self.handle_event(event):
                    running = False

            self.update(dt)

            if self.state == self.STATE_MENU:
                self.draw_menu()
            elif self.state == self.STATE_PLAYING:
                self.draw_game()
            elif self.state == self.STATE_OVER:
                self.draw_game_over()

            pygame.display.flip()

        pygame.quit()
        sys.exit()


# ============================================================
# 启动
# ============================================================
if __name__ == "__main__":
    game = TypingGame()
    game.run()
