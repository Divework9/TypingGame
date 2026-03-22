"""v0.0 基线功能回归测试（未引入键盘可视化前的核心玩法）。"""

import typing_game
from test.common import TypingGameBaseTestCase


class V00FeaturesTestCase(TypingGameBaseTestCase):
    def test_v00_core_loop_and_mode(self):
        self.assertEqual(self.game.mode, "english")
        self.assertEqual(self.game.lives, 5)
        self.assertEqual(self.game.level, 1)

        self.game.mode = "pinyin"
        self.game.spawn_word()
        self.assertGreaterEqual(len(self.game.words), 1)

    def test_v00_word_clear_and_miss(self):
        word = typing_game.FallingWord("cat", "cat", 100, 0, typing_game.TEXT_WHITE)
        self.game.words = [word]

        self.game.input_text = "cat"
        self.game.check_input()
        self.assertFalse(word.active)
        self.assertGreater(self.game.score, 0)

        miss_word = typing_game.FallingWord("dog", "dog", 100, 0, typing_game.TEXT_WHITE)
        self.game.lives = 2
        self.game.miss_word(miss_word)
        self.assertEqual(self.game.lives, 1)
