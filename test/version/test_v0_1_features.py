"""v0.1 功能测试：键盘可视化 + 配置文件化。"""

from conf.keyboard import (
    INPUT_PANEL_HEIGHT,
    KEYBOARD_PANEL_HEIGHT,
    FLASH_DURATION,
    get_keyboard_config_for_level,
)
from conf.speed import SPAWN_INTERVAL_BASE, FALL_SPEED_BASE
from conf.word_bank import ENGLISH_WORDS, PINYIN_WORDS

from test.common import TypingGameBaseTestCase


class V01FeaturesTestCase(TypingGameBaseTestCase):
    def test_v01_keyboard_profiles_available(self):
        level1 = get_keyboard_config_for_level(1)
        level2 = get_keyboard_config_for_level(2)
        level3 = get_keyboard_config_for_level(3)

        self.assertIn("layout", level1)
        self.assertIn("colors", level2)
        self.assertIn("metrics", level3)

        self.assertGreater(INPUT_PANEL_HEIGHT, 0)
        self.assertGreater(KEYBOARD_PANEL_HEIGHT, 0)
        self.assertGreater(FLASH_DURATION, 0)

    def test_v01_game_has_keyboard_runtime_state(self):
        self.assertGreater(len(self.game.keyboard_layout), 0)
        self.assertIsInstance(self.game.keyboard_colors, dict)
        self.assertIsInstance(self.game.keyboard_metrics, dict)
        self.assertIsInstance(self.game.key_flash, dict)

    def test_v01_speed_and_word_bank_loaded_from_conf(self):
        self.game.score = 0
        self.assertAlmostEqual(self.game.get_spawn_interval(), SPAWN_INTERVAL_BASE)
        self.assertAlmostEqual(self.game.get_fall_speed(), FALL_SPEED_BASE)

        self.assertIn("easy", ENGLISH_WORDS)
        self.assertIn("medium", ENGLISH_WORDS)
        self.assertIn("hard", ENGLISH_WORDS)
        self.assertIn("easy", PINYIN_WORDS)
        self.assertIn("medium", PINYIN_WORDS)
        self.assertIn("hard", PINYIN_WORDS)
