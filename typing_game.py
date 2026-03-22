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

你拿到后需要注意的事


"""

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
from conf.word_bank import ENGLISH_WORDS, PINYIN_WORDS

# ============================================================
# 初始化
# ============================================================
pygame.init()

SCREEN_W, SCREEN_H = 800, 600
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
            f.render("测试", True, (255, 255, 255))
            return f
        except:
            continue
    return pygame.font.Font(None, size)

font_big    = get_font(52, bold=True)
font_medium = get_font(36, bold=True)
font_small  = get_font(26)
font_tiny   = get_font(20)
font_input  = get_font(32, bold=True)

# ============================================================
# 游戏对象
# ============================================================
class FallingWord:
    def __init__(self, display_text, type_text, x, speed, color):
        self.display_text = display_text   # 屏幕上显示的文字
        self.type_text = type_text         # 需要输入的内容
        self.x = x
        self.y = -30
        self.speed = speed
        self.color = color
        self.matched_chars = 0             # 已匹配的字符数
        self.active = True

    def update(self, dt):
        self.y += self.speed * dt

    def is_out(self):
        return self.y > SCREEN_H - (BOTTOM_UI_HEIGHT + 15)

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
            pinyin_y = self.y + 40
            if typed:
                typed_surf = font_small.render(typed, True, MATCH_COLOR)
                surface.blit(typed_surf, (self.x, pinyin_y))
                offset = typed_surf.get_width()
            else:
                offset = 0
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
                offset = 0
            if remaining:
                remain_surf = font_medium.render(remaining, True, self.color)
                surface.blit(remain_surf, (self.x + offset, self.y))


class Particle:
    """消除特效粒子"""
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-150, 150)
        self.vy = random.uniform(-200, -50)
        self.life = 1.0
        self.color = color
        self.size = random.randint(3, 7)

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 300 * dt  # 重力
        self.life -= dt * 2
        return self.life > 0

    def draw(self, surface):
        alpha = max(0, int(self.life * 255))
        r, g, b = self.color
        s = max(1, int(self.size * self.life))
        pygame.draw.circle(surface, (r, g, b), (int(self.x), int(self.y)), s)


class Star:
    """背景星星"""
    def __init__(self):
        self.x = random.randint(0, SCREEN_W)
        self.y = random.randint(0, SCREEN_H)
        self.size = random.uniform(0.5, 2)
        self.blink_speed = random.uniform(1, 3)
        self.phase = random.uniform(0, 6.28)

    def draw(self, surface, t):
        import math
        brightness = 0.4 + 0.6 * (0.5 + 0.5 * math.sin(t * self.blink_speed + self.phase))
        c = int(255 * brightness)
        color = (c, c, int(c * 0.9))
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), max(1, int(self.size)))


# ============================================================
# 游戏主类
# ============================================================
class TypingGame:
    # 游戏状态
    STATE_MENU    = 0
    STATE_PLAYING = 1
    STATE_OVER    = 2

    def __init__(self):
        self.state = self.STATE_MENU
        self.mode = "english"         # "english" 或 "pinyin"
        self.score = 0
        self.lives = 5
        self.level = 1
        self.words = []               # 当前屏幕上的下落词
        self.particles = []
        self.input_text = ""
        self.combo = 0
        self.max_combo = 0
        self.words_cleared = 0
        self.words_missed = 0
        self.spawn_timer = 0
        self.game_time = 0
        self.stars = [Star() for _ in range(60)]
        self.shake_timer = 0          # 屏幕震动
        self.flash_timer = 0          # 消除闪光
        self.keyboard_layout = []
        self.keyboard_colors = {}
        self.keyboard_metrics = {}
        self.key_flash = {}
        self.apply_keyboard_config()

        # 菜单选项
        self.menu_selection = 0       # 0=英文, 1=拼音

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
                    self.key_flash[flash_key] = old_flash.get(flash_key, 0.0)

    def trigger_key_flash(self, letter):
        key = letter.lower()
        if key in self.key_flash:
            self.key_flash[key] = FLASH_DURATION

    def update_key_flash(self, dt):
        for key in self.key_flash:
            self.key_flash[key] = max(0, self.key_flash[key] - dt)

    def get_difficulty(self):
        if self.score < 100:
            return "easy"
        elif self.score < 300:
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

        if self.mode == "english":
            word = random.choice(ENGLISH_WORDS[diff])
            display = word
            type_text = word
        else:
            hanzi, pinyin = random.choice(PINYIN_WORDS[diff])
            display = hanzi
            # 去掉拼音中的数字标记(如 yu2 -> yu)
            type_text = ''.join(c for c in pinyin if not c.isdigit())

        # 计算文字宽度防止超出屏幕
        test_surf = font_medium.render(display, True, (255,255,255))
        max_x = SCREEN_W - test_surf.get_width() - 20
        x = random.randint(20, max(30, max_x))

        # 避免和已有词重叠
        for existing in self.words:
            if abs(existing.x - x) < 100 and existing.y < 60:
                x = random.randint(20, max(30, max_x))
                break

        self.words.append(FallingWord(display, type_text, x, speed, color))

    def check_input(self):
        """检查当前输入是否匹配任何下落词 - 使用滑动窗口前缀匹配"""
        if not self.input_text:
            for w in self.words:
                w.matched_chars = 0
            return

        input_lower = self.input_text.lower()

        for w in self.words:
            if not w.active:
                w.matched_chars = 0
                continue

            matched = 0
            should_clear = False
            for start_pos in range(len(input_lower)):
                substring = input_lower[start_pos:]
                if w.type_text.startswith(substring):
                    matched = len(substring)
                    if substring == w.type_text:
                        should_clear = True
                    break

            w.matched_chars = matched

            if should_clear:
                self.clear_word(w)
                self.input_text = ""
                return

    def clear_word(self, word):
        """消除一个词"""
        word.active = False

        # 计分
        base_score = len(word.type_text) * 10
        self.combo += 1
        combo_bonus = min(self.combo, 10) * 5
        self.score += base_score + combo_bonus
        self.words_cleared += 1
        self.max_combo = max(self.max_combo, self.combo)

        # 升级检测
        new_level = 1 + self.score // 150
        if new_level > self.level:
            self.level = new_level
            self.apply_keyboard_config()

        # 特效
        self.flash_timer = 0.15
        for _ in range(15):
            self.particles.append(Particle(
                word.x + random.randint(0, 80),
                word.y + 15,
                word.color
            ))

    def miss_word(self, word):
        """漏掉一个词"""
        word.active = False
        self.lives -= 1
        self.combo = 0
        self.words_missed += 1
        self.shake_timer = 0.3

        if self.lives <= 0:
            self.state = self.STATE_OVER

    def update(self, dt):
        if self.state != self.STATE_PLAYING:
            return

        self.game_time += dt
        self.shake_timer = max(0, self.shake_timer - dt)
        self.flash_timer = max(0, self.flash_timer - dt)
        self.update_key_flash(dt)

        # 生成新词
        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
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
        title_rect = title.get_rect(center=(SCREEN_W // 2, 120))
        screen.blit(title, title_rect)

        subtitle = font_small.render("Typing Adventure", True, TEXT_CYAN)
        sub_rect = subtitle.get_rect(center=(SCREEN_W // 2, 175))
        screen.blit(subtitle, sub_rect)

        # 模式选择
        mode_title = font_small.render("选择模式 / Select Mode:", True, TEXT_WHITE)
        screen.blit(mode_title, mode_title.get_rect(center=(SCREEN_W // 2, 260)))

        options = [
            ("🔤  英文单词模式  English Words", "english"),
            ("📝  中文拼音模式  Chinese Pinyin", "pinyin"),
        ]

        for i, (text, mode) in enumerate(options):
            y = 320 + i * 70
            is_selected = (i == self.menu_selection)

            if is_selected:
                # 选中框
                box_rect = pygame.Rect(SCREEN_W // 2 - 220, y - 10, 440, 50)
                pygame.draw.rect(screen, (60, 60, 120), box_rect, border_radius=10)
                pygame.draw.rect(screen, TEXT_CYAN, box_rect, 2, border_radius=10)
                color = TEXT_YELLOW
            else:
                color = (150, 150, 180)

            opt_surf = font_small.render(text, True, color)
            opt_rect = opt_surf.get_rect(center=(SCREEN_W // 2, y + 12))
            screen.blit(opt_surf, opt_rect)

        # 操作提示
        hints = [
            "↑↓ 选择模式    Enter 开始游戏",
            "打字消除下落的单词，别让它们落到底部！",
        ]
        for i, hint in enumerate(hints):
            h_surf = font_tiny.render(hint, True, (120, 120, 160))
            h_rect = h_surf.get_rect(center=(SCREEN_W // 2, 490 + i * 28))
            screen.blit(h_surf, h_rect)

    def draw_game(self):
        # 屏幕震动偏移
        import math
        if self.shake_timer > 0:
            ox = random.randint(-4, 4)
            oy = random.randint(-4, 4)
        else:
            ox, oy = 0, 0

        screen.fill(BG_COLOR)

        # 背景星星
        t = time.time()
        for star in self.stars:
            star.draw(screen, t)

        # 闪光效果
        if self.flash_timer > 0:
            flash_alpha = int(self.flash_timer / 0.15 * 40)
            flash_surf = pygame.Surface((SCREEN_W, SCREEN_H))
            flash_surf.fill((255, 255, 255))
            flash_surf.set_alpha(flash_alpha)
            screen.blit(flash_surf, (0, 0))

        # 顶部信息栏
        info_y = 8
        # 分数
        score_text = font_small.render(f"分数: {self.score}", True, TEXT_YELLOW)
        screen.blit(score_text, (15 + ox, info_y + oy))

        # 等级
        level_text = font_small.render(f"Lv.{self.level}", True, TEXT_CYAN)
        screen.blit(level_text, (200 + ox, info_y + oy))

        # Combo
        if self.combo > 1:
            combo_text = font_small.render(f"Combo x{self.combo}!", True, TEXT_ORANGE)
            screen.blit(combo_text, (300 + ox, info_y + oy))

        # 模式
        mode_label = "英文" if self.mode == "english" else "拼音"
        mode_text = font_tiny.render(f"[{mode_label}] Tab切换", True, (120, 120, 160))
        screen.blit(mode_text, (SCREEN_W - 170 + ox, info_y + 5 + oy))

        # 生命值
        heart_x = SCREEN_W - 170
        heart_y = info_y + 30
        for i in range(5):
            color = HEALTH_RED if i < self.lives else (60, 60, 60)
            pygame.draw.circle(screen, color, (heart_x + i * 30 + ox, heart_y + oy), 10)
            # 简单的心形：两个圆+一个三角
            pygame.draw.circle(screen, color, (heart_x + i * 30 - 5 + ox, heart_y - 4 + oy), 6)
            pygame.draw.circle(screen, color, (heart_x + i * 30 + 5 + ox, heart_y - 4 + oy), 6)

        # 分隔线
        pygame.draw.line(screen, (60, 60, 100), (0, 55), (SCREEN_W, 55), 1)

        # 下落词
        for w in self.words:
            w.draw(screen)

        # 粒子
        for p in self.particles:
            p.draw(screen)

        # 底部输入区域（上）
        input_area_y = SCREEN_H - BOTTOM_UI_HEIGHT
        pygame.draw.rect(screen, INPUT_BG, (0, input_area_y, SCREEN_W, INPUT_PANEL_HEIGHT))
        pygame.draw.line(screen, INPUT_BORDER, (0, input_area_y), (SCREEN_W, input_area_y), 2)

        # 输入框
        box_x, box_y = 20, input_area_y + 12
        box_w, box_h = SCREEN_W - 40, 40
        pygame.draw.rect(screen, (30, 30, 65), (box_x, box_y, box_w, box_h), border_radius=8)
        pygame.draw.rect(screen, INPUT_BORDER, (box_x, box_y, box_w, box_h), 2, border_radius=8)

        # 输入文字
        if self.input_text:
            input_surf = font_input.render(self.input_text, True, TEXT_WHITE)
        else:
            placeholder = "输入单词消除它们..." if self.mode == "english" else "输入拼音消除汉字..."
            input_surf = font_input.render(placeholder, True, (80, 80, 120))
        screen.blit(input_surf, (box_x + 12, box_y + 5))

        # 光标闪烁
        if self.input_text or int(time.time() * 2) % 2:
            cursor_x = box_x + 14 + font_input.size(self.input_text)[0]
            pygame.draw.rect(screen, TEXT_WHITE, (cursor_x, box_y + 6, 2, 28))

        # 底部键盘区域（下）
        keyboard_area_y = input_area_y + INPUT_PANEL_HEIGHT
        pygame.draw.rect(screen, (30, 30, 70), (0, keyboard_area_y, SCREEN_W, KEYBOARD_PANEL_HEIGHT))
        pygame.draw.line(screen, INPUT_BORDER, (0, keyboard_area_y), (SCREEN_W, keyboard_area_y), 1)
        self.draw_keyboard(keyboard_area_y + 4, ox, oy)

    def draw_keyboard(self, start_y, ox=0, oy=0):
        unit_w = self.keyboard_metrics["unit_w"]
        key_h = self.keyboard_metrics["key_h"]
        gap_x = self.keyboard_metrics["gap_x"]
        gap_y = self.keyboard_metrics["gap_y"]

        for row_index, row in enumerate(self.keyboard_layout):
            row_width = sum(int(unit_w * key["width"]) for key in row) + gap_x * (len(row) - 1)
            start_x = (SCREEN_W - row_width) // 2
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
                is_flashing = flash_key in self.key_flash and self.key_flash[flash_key] > 0
                if is_flashing:
                    flash_boost = self.keyboard_colors["flash_boost"]
                    fill_color = (
                        min(255, base_fill[0] + flash_boost),
                        min(255, base_fill[1] + flash_boost),
                        min(255, base_fill[2] + flash_boost),
                    )
                    border_color = self.keyboard_colors["flash_border"]
                else:
                    fill_color = base_fill
                    border_color = base_border

                rect = pygame.Rect(x + ox, y + oy, key_w, key_h)
                pygame.draw.rect(screen, fill_color, rect, border_radius=4)
                pygame.draw.rect(screen, border_color, rect, 1, border_radius=4)

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
        title_rect = title.get_rect(center=(SCREEN_W // 2, 100))
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
            color = TEXT_YELLOW if i == 0 else TEXT_WHITE
            s = font_small.render(stat, True, color)
            r = s.get_rect(center=(SCREEN_W // 2, 200 + i * 40))
            screen.blit(s, r)

        # 评价
        if self.score >= 500:
            comment = "太厉害了！打字高手！🌟"
            c_color = TEXT_YELLOW
        elif self.score >= 200:
            comment = "不错哦！继续加油！💪"
            c_color = TEXT_GREEN
        else:
            comment = "多练习就会越来越好！📖"
            c_color = TEXT_CYAN

        comment_surf = font_medium.render(comment, True, c_color)
        comment_rect = comment_surf.get_rect(center=(SCREEN_W // 2, 430))
        screen.blit(comment_surf, comment_rect)

        # 提示
        hint = font_small.render("按 Enter 重新开始    按 Esc 返回菜单", True, (120, 120, 160))
        hint_rect = hint.get_rect(center=(SCREEN_W // 2, 520))
        screen.blit(hint, hint_rect)

    def reset_game(self):
        self.score = 0
        self.lives = 5
        self.level = 1
        self.words = []
        self.particles = []
        self.input_text = ""
        self.combo = 0
        self.max_combo = 0
        self.words_cleared = 0
        self.words_missed = 0
        self.spawn_timer = 1.0
        self.game_time = 0
        self.shake_timer = 0
        self.flash_timer = 0
        self.apply_keyboard_config()
        for key in self.key_flash:
            self.key_flash[key] = 0

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            return False

        if event.type == pygame.KEYDOWN:
            if self.state == self.STATE_MENU:
                if event.key == pygame.K_UP:
                    self.menu_selection = (self.menu_selection - 1) % 2
                elif event.key == pygame.K_DOWN:
                    self.menu_selection = (self.menu_selection + 1) % 2
                elif event.key == pygame.K_RETURN:
                    self.mode = "english" if self.menu_selection == 0 else "pinyin"
                    self.reset_game()
                    self.state = self.STATE_PLAYING

            elif self.state == self.STATE_PLAYING:
                if event.unicode and event.unicode.lower() in self.key_flash:
                    self.trigger_key_flash(event.unicode)

                if event.key == pygame.K_ESCAPE:
                    self.state = self.STATE_MENU
                elif event.key == pygame.K_TAB:
                    # 切换模式
                    self.mode = "pinyin" if self.mode == "english" else "english"
                    self.input_text = ""
                    for w in self.words:
                        w.matched_chars = 0
                elif event.key == pygame.K_BACKSPACE:
                    self.input_text = self.input_text[:-1]
                    self.check_input()
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    # 回车/空格清空输入（不匹配时重来）
                    self.input_text = ""
                    for w in self.words:
                        w.matched_chars = 0
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
            dt = clock.tick(60) / 1000.0
            dt = min(dt, 0.05)  # 防止跳帧

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
