import typing_game
from test.common import TypingGameBaseTestCase


class ProgressionStateTestCase(TypingGameBaseTestCase):
    def test_clear_word_updates_combo_score_and_level(self):
        self.game.score = 145
        word = typing_game.FallingWord("apple", "apple", 100, 0, typing_game.TEXT_WHITE)

        self.game.clear_word(word)

        self.assertFalse(word.active)
        self.assertEqual(self.game.combo, 1)
        self.assertEqual(self.game.max_combo, 1)
        self.assertEqual(self.game.words_cleared, 1)
        self.assertEqual(self.game.score, 200)
        self.assertEqual(self.game.level, 2)

    def test_miss_word_reduces_life_and_ends_game(self):
        word = typing_game.FallingWord("cat", "cat", 100, 0, typing_game.TEXT_WHITE)
        self.game.lives = 1

        self.game.miss_word(word)

        self.assertFalse(word.active)
        self.assertEqual(self.game.lives, 0)
        self.assertEqual(self.game.state, self.game.STATE_OVER)

    def test_update_removes_inactive_words(self):
        self.game.words = [typing_game.FallingWord("cat", "cat", 100, 0, typing_game.TEXT_WHITE)]
        self.game.words[0].active = False
        self.game.spawn_timer = 999

        self.game.update(0.016)

        self.assertEqual(len(self.game.words), 0)
