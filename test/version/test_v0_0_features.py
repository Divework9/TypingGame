"""v0.0 基线功能回归测试（未引入键盘可视化前的核心玩法）。"""

from test.common import TypingGameBaseTestCase
import typing_game


class V00FeaturesTestCase(TypingGameBaseTestCase):
    def test_v00_core_loop_and_mode(self):
        # Initial state assertions
        self.assertEqual(self.game.mode, "english")
        self.assertEqual(self.game.lives, 5)
        self.assertEqual(self.game.level, 1)
        self.assertEqual(self.game.score, 0)
        self.assertEqual(self.game.combo, 0)

        # Pinyin mode spawns a word where display_text (hanzi) != type_text (pinyin)
        self.game.mode = "pinyin"
        self.game.spawn_word()
        self.assertEqual(len(self.game.words), 1)
        word = self.game.words[0]
        self.assertNotEqual(word.display_text, word.type_text)
        # tone digits must be stripped from type_text
        self.assertFalse(any(c.isdigit() for c in word.type_text))

    def test_v00_word_clear_and_miss(self):
        word = typing_game.FallingWord("cat", "cat", 100, 0, typing_game.TEXT_WHITE)
        self.game.words = [word]

        self.game.input_text = "cat"
        self.game.check_input()
        self.assertFalse(word.active)
        self.assertGreater(self.game.score, 0)
        self.assertEqual(self.game.words_cleared, 1)

        miss_word = typing_game.FallingWord("dog", "dog", 100, 0, typing_game.TEXT_WHITE)
        self.game.lives = 2
        self.game.miss_word(miss_word)
        self.assertEqual(self.game.lives, 1)
        self.assertEqual(self.game.state, self.game.STATE_PLAYING)
