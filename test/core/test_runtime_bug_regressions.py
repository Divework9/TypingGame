"""运行中发现问题的回归测试集合。

约定：
- 任何在实际运行中发现并修复的 bug，都在这里补一条最小可复现测试。
- 测试命名建议：test_bug_<日期或编号>_<现象描述>
- 这个文件只放“回归类”测试，避免和功能主线测试混杂。
"""

import importlib
import os

from conf import combo_feedback as cf
import typing_game
from test.common import TypingGameBaseTestCase


class RuntimeBugRegressionTestCase(TypingGameBaseTestCase):
    def test_combo_feedback_tier_step_and_cap(self):
        """回归：鼓励词按每5个 combo 分档，且第6档后封顶。"""
        self.assertEqual(cf.get_feedback_tier_index(1), -1)
        self.assertEqual(cf.get_feedback_tier_index(2), 0)
        self.assertEqual(cf.get_feedback_tier_index(5), 0)
        self.assertEqual(cf.get_feedback_tier_index(6), 1)
        self.assertEqual(cf.get_feedback_tier_index(10), 1)
        self.assertEqual(cf.get_feedback_tier_index(11), 2)
        self.assertEqual(cf.get_feedback_tier_index(26), 5)
        self.assertEqual(cf.get_feedback_tier_index(99), 5)

    def test_combo_feedback_changes_on_each_combo_increment(self):
        """回归：combo 每次+1时，鼓励词应更新（同档内不重复上一词）。"""
        previous = ""
        seen = []
        for combo in [2, 3, 4, 5, 6, 7]:
            current = cf.choose_combo_feedback(combo, previous)
            self.assertNotEqual(current, "")
            if previous:
                self.assertNotEqual(current, previous)
            seen.append(current)
            previous = current
        self.assertGreaterEqual(len(set(seen)), 3)

    def _assert_heart_geometry_for_scale(self, scale_ratio):
        """在给定缩放倍率下检查红心几何比例与边界。"""
        original_scale = os.environ.get("TYPING_GAME_SCALE_RATIO")
        try:
            os.environ["TYPING_GAME_SCALE_RATIO"] = str(scale_ratio)

            import conf.game_constants as gc_mod
            import typing_game as tg_mod

            gc_mod = importlib.reload(gc_mod)
            tg_mod = importlib.reload(tg_mod)

            # 按主程序绘制公式还原红心关键几何点
            heart_x = gc_mod.SCREEN_WIDTH - gc_mod.HEART_PANEL_RIGHT_OFFSET
            heart_y = gc_mod.TOP_INFO_Y + gc_mod.HEART_PANEL_Y_OFFSET

            first_center_x = heart_x
            last_center_x = heart_x + (gc_mod.HEART_COUNT - 1) * gc_mod.HEART_GAP
            left_lobe_x = first_center_x - gc_mod.HEART_LOBE_X_OFFSET
            right_lobe_x = last_center_x + gc_mod.HEART_LOBE_X_OFFSET
            lobe_y = heart_y - gc_mod.HEART_LOBE_Y_OFFSET
            top_y = lobe_y - gc_mod.HEART_LOBE_RADIUS
            bottom_y = heart_y + gc_mod.HEART_MAIN_RADIUS + gc_mod.HEART_LOBE_RADIUS

            # 1) 几何比例：下尖必须在上半圆下方；上半圆水平不应过度分离
            self.assertGreater(bottom_y, lobe_y)
            self.assertLessEqual(gc_mod.HEART_LOBE_X_OFFSET, gc_mod.HEART_LOBE_RADIUS * 2)

            # 2) 屏幕边界：整排红心在屏幕内
            self.assertGreaterEqual(left_lobe_x - gc_mod.HEART_LOBE_RADIUS, 0)
            self.assertLessEqual(right_lobe_x + gc_mod.HEART_LOBE_RADIUS, gc_mod.SCREEN_WIDTH)
            self.assertGreaterEqual(top_y, 0)
            self.assertLessEqual(bottom_y, gc_mod.SCREEN_HEIGHT)
        finally:
            if original_scale is None:
                os.environ.pop("TYPING_GAME_SCALE_RATIO", None)
            else:
                os.environ["TYPING_GAME_SCALE_RATIO"] = original_scale

            import conf.game_constants as gc_mod
            import typing_game as tg_mod
            importlib.reload(gc_mod)
            importlib.reload(tg_mod)

    def test_bug_spawn_timer_reset_prevents_continuous_spawn(self):
        """回归：spawn 后必须重置计时器，避免每帧都生成新词。"""
        self.game.words = []
        self.game.spawn_timer = 0  # 首帧触发生成

        self.game.update(0)
        first_count = len(self.game.words)

        # 第二帧 dt=0，不应继续生成（若没有重置计时器会持续增长）
        self.game.update(0)
        second_count = len(self.game.words)

        self.assertEqual(first_count, 1)
        self.assertEqual(second_count, 1)

    def test_bug_update_in_over_state_does_not_advance_game_time(self):
        """回归：游戏结束态 update 必须 no-op。"""
        self.game.state = self.game.STATE_OVER
        self.game.game_time = 0.0

        self.game.update(0.5)

        self.assertAlmostEqual(self.game.game_time, 0.0)

    def test_bug_duplicate_word_should_clear_bottom_one_first(self):
        """复现：同词同时存在时，应优先消除更靠近底部（y更大）的那个。"""
        top_word = typing_game.FallingWord("cat", "cat", 100, 0, typing_game.TEXT_WHITE)
        bottom_word = typing_game.FallingWord("cat", "cat", 100, 0, typing_game.TEXT_WHITE)
        top_word.y = 120
        bottom_word.y = 320

        # 故意把上方词放在列表前，暴露当前“按列表顺序”清除的问题
        self.game.words = [top_word, bottom_word]

        self.game.input_text = "cat"
        self.game.check_input()

        self.assertTrue(top_word.active)
        self.assertFalse(bottom_word.active)

    def test_bug_duplicate_word_remaining_one_should_not_keep_partial_highlight(self):
        """复现：消除其中一个后，另一个同词不应保留旧的 matched_chars 高亮。"""
        word1 = typing_game.FallingWord("cat", "cat", 100, 0, typing_game.TEXT_WHITE)
        word2 = typing_game.FallingWord("cat", "cat", 200, 0, typing_game.TEXT_WHITE)
        self.game.words = [word1, word2]

        # 先制造“两个词都局部高亮”的状态
        self.game.input_text = "ca"
        self.game.check_input()
        self.assertEqual(word1.matched_chars, 2)
        self.assertEqual(word2.matched_chars, 2)

        # 再完整输入触发清除一个词
        self.game.input_text = "cat"
        self.game.check_input()

        remaining = word1 if word1.active else word2
        self.assertEqual(self.game.input_text, "")
        self.assertEqual(remaining.matched_chars, 0)

    def test_bug_scale_50_keyboard_label_should_not_be_clipped(self):
        """回归：50% 缩放下，键帽可用高度必须容纳标签字高。"""
        original_scale = os.environ.get("TYPING_GAME_SCALE_RATIO")
        try:
            os.environ["TYPING_GAME_SCALE_RATIO"] = "0.5"

            import conf.game_constants as gc_mod
            import conf.keyboard as kb_mod
            import typing_game as tg_mod

            gc_mod = importlib.reload(gc_mod)
            kb_mod = importlib.reload(kb_mod)
            tg_mod = importlib.reload(tg_mod)

            keyboard_cfg = kb_mod.get_keyboard_config_for_level(3)
            key_h = keyboard_cfg["metrics"]["key_h"]
            key_available_height = key_h - 2 * gc_mod.KEYBOARD_KEY_BORDER_WIDTH
            key_label_height = tg_mod.font_tiny.get_height()

            self.assertGreaterEqual(
                key_available_height,
                key_label_height,
                msg=(
                    "50% 缩放下键帽高度不足，标签可能被裁切: "
                    f"available={key_available_height}, label={key_label_height}"
                ),
            )
        finally:
            if original_scale is None:
                os.environ.pop("TYPING_GAME_SCALE_RATIO", None)
            else:
                os.environ["TYPING_GAME_SCALE_RATIO"] = original_scale

            import conf.game_constants as gc_mod
            import conf.keyboard as kb_mod
            import typing_game as tg_mod
            importlib.reload(gc_mod)
            importlib.reload(kb_mod)
            importlib.reload(tg_mod)

    def test_bug_scale_heart_shape_should_adapt_across_50_to_200(self):
        """回归：红心在 50% / 200% 缩放下应保持有效几何并在屏幕内。"""
        with self.subTest(scale=0.5):
            self._assert_heart_geometry_for_scale(0.5)
        with self.subTest(scale=2.0):
            self._assert_heart_geometry_for_scale(2.0)
