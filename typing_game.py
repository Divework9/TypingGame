"""
打字练习小游戏 - 适合小学4-6年级
英文单词 + 中文拼音 下落消除模式

依赖: pip install pygame
运行: python typing_game.py
"""

import pygame
import random
import sys
import time

# ============================================================
# 初始化
# ============================================================
pygame.init()

SCREEN_W, SCREEN_H = 800, 600
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("⌨️ 打字大冒险 - Typing Adventure")
clock = pygame.time.Clock()

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
# 词库
# ============================================================
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
        return self.y > SCREEN_H - 80

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

        # 菜单选项
        self.menu_selection = 0       # 0=英文, 1=拼音

    def get_difficulty(self):
        if self.score < 100:
            return "easy"
        elif self.score < 300:
            return "medium"
        else:
            return "hard"

    def get_spawn_interval(self):
        """根据分数动态调整生成间隔"""
        base = 2.5
        reduction = self.score * 0.003
        return max(0.8, base - reduction)

    def get_fall_speed(self):
        """根据分数动态调整下落速度"""
        base = 40
        increase = self.score * 0.08
        return min(120, base + increase)

    def spawn_word(self):
        diff = self.get_difficulty()
        speed = self.get_fall_speed() + random.uniform(-10, 10)
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
        """检查当前输入是否匹配任何下落词"""
        if not self.input_text:
            # 清空所有词的部分匹配
            for w in self.words:
                w.matched_chars = 0
            return

        best_match = None
        best_match_len = 0

        for w in self.words:
            if not w.active:
                continue
            # 检查输入是否是该词的前缀
            if w.type_text.startswith(self.input_text.lower()):
                w.matched_chars = len(self.input_text)
                if len(self.input_text) > best_match_len:
                    best_match = w
                    best_match_len = len(self.input_text)

                # 完全匹配 -> 消除
                if self.input_text.lower() == w.type_text:
                    self.clear_word(w)
                    self.input_text = ""
                    return
            else:
                w.matched_chars = 0

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

        # 底部输入区域
        input_area_y = SCREEN_H - 65
        pygame.draw.rect(screen, INPUT_BG, (0, input_area_y, SCREEN_W, 65))
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
                    self.input_text += event.unicode.lower()
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
