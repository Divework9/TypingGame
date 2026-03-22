import importlib
import os

from conf import game_constants as gc
from conf.keyboard import get_keyboard_config_for_level
from test.common import TypingGameBaseTestCase
import typing_game


class LayoutBoundsTestCase(TypingGameBaseTestCase):
    """布局边界回归测试：用于检出字体放大后容器/边框不适配问题。"""

    def _assert_top_info_non_overlap_for_scale(self, scale_ratio):
        """在给定缩放倍率下校验顶部信息栏关键元素不重叠。"""
        original_value = os.environ.get("TYPING_GAME_SCALE_RATIO")
        try:
            os.environ["TYPING_GAME_SCALE_RATIO"] = str(scale_ratio)

            import conf.game_constants as gc_mod
            import typing_game as tg_mod

            gc_mod = importlib.reload(gc_mod)
            tg_mod = importlib.reload(tg_mod)

            info_y = gc_mod.TOP_INFO_Y

            # 左侧信息：分数 / 等级 / 连击 应按 x 轴顺序留有间隔
            score_text = tg_mod.font_small.render("分数: 9999", True, tg_mod.TEXT_WHITE)
            level_text = tg_mod.font_small.render("Lv.99", True, tg_mod.TEXT_WHITE)
            combo_text = tg_mod.font_small.render("Combo x99!", True, tg_mod.TEXT_WHITE)

            score_left = gc_mod.SCORE_TEXT_X
            score_right = score_left + score_text.get_width()
            level_left = gc_mod.LEVEL_TEXT_X
            level_right = level_left + level_text.get_width()
            combo_left = gc_mod.COMBO_TEXT_X
            combo_right = combo_left + combo_text.get_width()

            self.assertLessEqual(score_right, level_left)
            self.assertLessEqual(level_right, combo_left)
            self.assertLessEqual(combo_right, gc_mod.SCREEN_WIDTH)

            # 右侧信息：模式提示 与 红心区域不应发生矩形相交
            mode_text = tg_mod.font_tiny.render("[英文] Tab切换", True, tg_mod.TEXT_WHITE)
            mode_rect = mode_text.get_rect(
                topleft=(
                    gc_mod.SCREEN_WIDTH - gc_mod.MODE_HINT_RIGHT_OFFSET,
                    info_y + gc_mod.MODE_HINT_Y_OFFSET,
                )
            )

            heart_x = gc_mod.SCREEN_WIDTH - gc_mod.HEART_PANEL_RIGHT_OFFSET
            heart_y = info_y + gc_mod.HEART_PANEL_Y_OFFSET
            heart_left = heart_x - gc_mod.HEART_LOBE_X_OFFSET - gc_mod.HEART_LOBE_RADIUS
            heart_right = (
                heart_x
                + (gc_mod.HEART_COUNT - 1) * gc_mod.HEART_GAP
                + gc_mod.HEART_LOBE_X_OFFSET
                + gc_mod.HEART_LOBE_RADIUS
            )
            heart_top = heart_y - gc_mod.HEART_LOBE_Y_OFFSET - gc_mod.HEART_LOBE_RADIUS
            heart_bottom = heart_y + gc_mod.HEART_MAIN_RADIUS + gc_mod.HEART_LOBE_RADIUS

            heart_rect = tg_mod.pygame.Rect(
                heart_left,
                heart_top,
                heart_right - heart_left,
                heart_bottom - heart_top,
            )

            self.assertFalse(mode_rect.colliderect(heart_rect))
        finally:
            if original_value is None:
                os.environ.pop("TYPING_GAME_SCALE_RATIO", None)
            else:
                os.environ["TYPING_GAME_SCALE_RATIO"] = original_value

            import conf.game_constants as gc_mod
            import typing_game as tg_mod
            importlib.reload(gc_mod)
            importlib.reload(tg_mod)

    def _assert_layout_bounds_for_scale(self, scale_ratio):
        """在给定缩放倍率下重载模块并检查核心布局边界。"""
        original_value = os.environ.get("TYPING_GAME_SCALE_RATIO")
        try:
            os.environ["TYPING_GAME_SCALE_RATIO"] = str(scale_ratio)

            # 必须按依赖顺序重载，确保常量 -> 键盘 -> 主程序全部使用新缩放比例
            import conf.game_constants as gc_mod
            import conf.keyboard as kb_mod
            import typing_game as tg_mod

            gc_mod = importlib.reload(gc_mod)
            kb_mod = importlib.reload(kb_mod)
            tg_mod = importlib.reload(tg_mod)

            # 1) 输入区：字体高度不应超过输入框可用高度（可检出“字体放大但输入框未放大”）
            input_text_height = tg_mod.font_input.get_height()
            input_available_height = gc_mod.INPUT_BOX_HEIGHT - 2 * gc_mod.INPUT_TEXT_Y_OFFSET
            self.assertGreaterEqual(input_available_height, input_text_height)

            # 2) 菜单选项：文字高度应落在选中框边界内（可检出“文字放大但选中框未放大”）
            option_texts = [
                "🔤  英文单词模式  English Words",
                "📝  中文拼音模式  Chinese Pinyin",
            ]
            max_option_text_h = max(tg_mod.font_small.size(text)[1] for text in option_texts)
            box_top = -gc_mod.MENU_BOX_Y_OFFSET
            box_bottom = -gc_mod.MENU_BOX_Y_OFFSET + gc_mod.MENU_BOX_HEIGHT
            text_top = gc_mod.MENU_OPTION_TEXT_Y_OFFSET - max_option_text_h / 2
            text_bottom = gc_mod.MENU_OPTION_TEXT_Y_OFFSET + max_option_text_h / 2
            self.assertGreaterEqual(text_top, box_top)
            self.assertLessEqual(text_bottom, box_bottom)

            # 3) 键盘：标签字高应在按键高度边界内（可检出“字体放大但 key_h 未放大”）
            keyboard_cfg = kb_mod.get_keyboard_config_for_level(3)
            key_h = keyboard_cfg["metrics"]["key_h"]
            key_available_height = key_h - 2 * gc_mod.KEYBOARD_KEY_BORDER_WIDTH
            key_label_height = tg_mod.font_tiny.get_height()
            self.assertGreaterEqual(key_available_height, key_label_height)

            # 4) 底部区域总高度应在屏幕内
            bottom_ui_height = gc_mod.INPUT_PANEL_HEIGHT + gc_mod.KEYBOARD_PANEL_HEIGHT
            self.assertLess(bottom_ui_height, gc_mod.SCREEN_HEIGHT)

            # 5) 光标应与输入字母尺寸/位置一致（可检出“光标缩放未跟随输入字体”）
            sample_text = "typing"
            game = tg_mod.TypingGame()
            game.state = game.STATE_PLAYING
            game.input_text = sample_text

            input_area_y = gc_mod.SCREEN_HEIGHT - (gc_mod.INPUT_PANEL_HEIGHT + gc_mod.KEYBOARD_PANEL_HEIGHT)
            box_x = gc_mod.INPUT_BOX_X
            box_y = input_area_y + gc_mod.INPUT_BOX_Y_OFFSET
            box_h = gc_mod.INPUT_BOX_HEIGHT

            cursor_rect = game._compute_input_cursor_rect(box_x, box_y, box_h)
            text_left = box_x + gc_mod.INPUT_TEXT_X_OFFSET
            text_top = box_y + gc_mod.INPUT_TEXT_Y_OFFSET
            text_w, text_h = tg_mod.font_input.size(sample_text)
            text_end = text_left + text_w
            text_bottom = text_top + text_h

            # 光标应与文字底部基本对齐（允许 1 像素误差）
            self.assertLessEqual(abs(cursor_rect.bottom - text_bottom), 1)

            # 光标应位于文字区域附近，且不应跑到文字框外
            self.assertGreaterEqual(cursor_rect.top, text_top)
            self.assertLessEqual(cursor_rect.bottom, text_bottom + 1)

            cursor_text_delta = cursor_rect.left - text_end
            self.assertGreaterEqual(cursor_text_delta, 0)
            self.assertLessEqual(cursor_text_delta, max(gc_mod.CURSOR_WIDTH * 3, int(round(4 * scale_ratio))))
        finally:
            if original_value is None:
                os.environ.pop("TYPING_GAME_SCALE_RATIO", None)
            else:
                os.environ["TYPING_GAME_SCALE_RATIO"] = original_value

            # 还原默认缩放模块状态，避免影响后续测试
            import conf.game_constants as gc_mod
            import conf.keyboard as kb_mod
            import typing_game as tg_mod
            importlib.reload(gc_mod)
            importlib.reload(kb_mod)
            importlib.reload(tg_mod)

    def test_input_font_height_fits_input_box_with_padding(self):
        """回归检出1：字体放大后，输入框高度必须同步可容纳文字。"""
        text_height = typing_game.font_input.get_height()
        available_height = gc.INPUT_BOX_HEIGHT - 2 * gc.INPUT_TEXT_Y_OFFSET
        self.assertGreaterEqual(
            available_height,
            text_height,
            msg=(
                f"输入框可用高度不足: available={available_height}, text={text_height}. "
                "若仅放大字体而不放大输入框，会触发该失败。"
            ),
        )

    def test_cursor_height_fits_input_box(self):
        """输入光标高度必须在输入框内，避免视觉溢出。"""
        available_height = gc.INPUT_BOX_HEIGHT - 2 * gc.CURSOR_Y_OFFSET
        self.assertGreaterEqual(
            available_height,
            gc.CURSOR_HEIGHT,
            msg=(
                f"光标高度超出输入框: available={available_height}, cursor={gc.CURSOR_HEIGHT}"
            ),
        )

    def test_cursor_matches_input_letters_at_50_and_200_percent(self):
        """边界测试：光标在 50%/200% 缩放下应与输入字母高度和位置匹配。"""
        with self.subTest(scale=0.5):
            self._assert_layout_bounds_for_scale(0.5)
        with self.subTest(scale=2.0):
            self._assert_layout_bounds_for_scale(2.0)

    def test_menu_option_text_fits_selection_box_height(self):
        """回归检出2：菜单选项字高放大后，必须仍在选中框高度边界内。"""
        option_texts = [
            "🔤  英文单词模式  English Words",
            "📝  中文拼音模式  Chinese Pinyin",
        ]
        max_text_height = max(typing_game.font_small.size(text)[1] for text in option_texts)

        box_top = -gc.MENU_BOX_Y_OFFSET
        box_bottom = -gc.MENU_BOX_Y_OFFSET + gc.MENU_BOX_HEIGHT
        text_top = gc.MENU_OPTION_TEXT_Y_OFFSET - max_text_height / 2
        text_bottom = gc.MENU_OPTION_TEXT_Y_OFFSET + max_text_height / 2

        self.assertGreaterEqual(
            text_top,
            box_top,
            msg=(
                f"选项文字上边越界: text_top={text_top}, box_top={box_top}. "
                "若只放大字体不调整选中框，会触发该失败。"
            ),
        )
        self.assertLessEqual(
            text_bottom,
            box_bottom,
            msg=(
                f"选项文字下边越界: text_bottom={text_bottom}, box_bottom={box_bottom}. "
                "若只放大字体不调整选中框，会触发该失败。"
            ),
        )

    def test_menu_option_text_fits_selection_box_width_with_border(self):
        """菜单选项最长文本应在选中框（扣除边框）内显示。"""
        option_texts = [
            "🔤  英文单词模式  English Words",
            "📝  中文拼音模式  Chinese Pinyin",
        ]
        max_text_width = max(typing_game.font_small.size(text)[0] for text in option_texts)
        available_width = gc.MENU_BOX_WIDTH - 2 * gc.MENU_OPTION_COUNT

        self.assertGreaterEqual(
            available_width,
            max_text_width,
            msg=(
                f"选中框宽度不足: available={available_width}, text={max_text_width}"
            ),
        )

    def test_keyboard_label_font_fits_key_height_with_border(self):
        """回归检出3：键帽文字高度必须可容纳于按键高度与边框内。"""
        keyboard_config = get_keyboard_config_for_level(3)
        key_h = keyboard_config["metrics"]["key_h"]
        label_height = typing_game.font_tiny.get_height()
        available_height = key_h - 2 * gc.KEYBOARD_KEY_BORDER_WIDTH

        self.assertGreaterEqual(
            available_height,
            label_height,
            msg=(
                f"键帽高度不足: available={available_height}, label={label_height}. "
                "若只放大字体不调整 key_h，会触发该失败。"
            ),
        )

    def test_keyboard_label_font_fits_single_unit_key_width(self):
        """单字符标签在 1.0 单位宽按键内应可容纳。"""
        keyboard_config = get_keyboard_config_for_level(3)
        unit_w = keyboard_config["metrics"]["unit_w"]
        key_w = int(unit_w * 1.0)
        label_width = typing_game.font_tiny.size("W")[0]
        available_width = key_w - 2 * gc.KEYBOARD_KEY_BORDER_WIDTH

        self.assertGreaterEqual(
            available_width,
            label_width,
            msg=f"按键宽度不足: available={available_width}, label={label_width}",
        )

    def test_bottom_ui_panels_stay_within_screen_height(self):
        """底部输入区+键盘区总高度必须小于屏幕高度。"""
        bottom_ui_height = gc.INPUT_PANEL_HEIGHT + gc.KEYBOARD_PANEL_HEIGHT
        self.assertLess(
            bottom_ui_height,
            gc.SCREEN_HEIGHT,
            msg=(
                f"底部UI过高: bottom_ui={bottom_ui_height}, screen={gc.SCREEN_HEIGHT}"
            ),
        )

    def test_layout_bounds_at_min_scale_50_percent(self):
        """边界测试：缩放到 50% 时布局仍应满足边界约束。"""
        self._assert_layout_bounds_for_scale(0.5)

    def test_layout_bounds_at_max_scale_200_percent(self):
        """边界测试：缩放到 200% 时布局仍应满足边界约束。"""
        self._assert_layout_bounds_for_scale(2.0)

    def test_top_info_elements_non_overlap_at_50_and_200_percent(self):
        """顶部信息栏在 50%/200% 缩放下不应发生关键元素重叠。"""
        with self.subTest(scale=0.5):
            self._assert_top_info_non_overlap_for_scale(0.5)
        with self.subTest(scale=2.0):
            self._assert_top_info_non_overlap_for_scale(2.0)
