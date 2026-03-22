"""v0.1 功能测试：键盘可视化 + 配置文件化。"""

from conf.keyboard import (
    INPUT_PANEL_HEIGHT,
    KEYBOARD_PANEL_HEIGHT,
    FLASH_DURATION,
    get_keyboard_config_for_level,
)

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

    def test_v01_trigger_key_flash_sets_duration(self):
        flash_keys = list(self.game.key_flash.keys())
        self.assertGreater(len(flash_keys), 0, "Level 1 should have at least one flash key")
        key = flash_keys[0]
        # starts at 0.0 (no flash)
        self.assertAlmostEqual(self.game.key_flash[key], 0.0)

        self.game.trigger_key_flash(key)

        self.assertAlmostEqual(self.game.key_flash[key], FLASH_DURATION)

    def test_v01_update_key_flash_decrements_timer(self):
        flash_keys = list(self.game.key_flash.keys())
        self.assertGreater(len(flash_keys), 0)
        key = flash_keys[0]
        self.game.trigger_key_flash(key)

        self.game.update_key_flash(0.05)

        self.assertAlmostEqual(self.game.key_flash[key], FLASH_DURATION - 0.05, places=5)

    def test_v01_update_key_flash_does_not_go_below_zero(self):
        flash_keys = list(self.game.key_flash.keys())
        self.assertGreater(len(flash_keys), 0)
        key = flash_keys[0]
        self.game.trigger_key_flash(key)

        self.game.update_key_flash(FLASH_DURATION * 10)  # far exceeds flash duration

        self.assertEqual(self.game.key_flash[key], 0.0)

    # R2-09: trigger_key_flash is silent no-op for keys not in the flash set
    def test_v01_trigger_key_flash_noop_for_unknown_key(self):
        flash_keys_before = dict(self.game.key_flash)

        self.game.trigger_key_flash("@")  # not a real keyboard key

        self.assertEqual(self.game.key_flash, flash_keys_before)  # unchanged

    # R2-10: apply_keyboard_config preserves in-flight flash timers across level-up
    def test_v01_apply_keyboard_config_preserves_flash_timers_on_levelup(self):
        flash_keys = list(self.game.key_flash.keys())
        self.assertGreater(len(flash_keys), 0)
        key = flash_keys[0]

        # set a live flash timer
        self.game.key_flash[key] = 0.12

        # level-up reloads keyboard config
        new_level = self.game.level + 1
        self.game.level = new_level
        self.game.apply_keyboard_config()

        # the key that was flashing should retain its timer if it exists in the new layout
        if key in self.game.key_flash:
            self.assertAlmostEqual(self.game.key_flash[key], 0.12)
