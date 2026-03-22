import os
import unittest
from unittest.mock import patch
from conf.speed import (
    SPAWN_INTERVAL_BASE,
    SPAWN_INTERVAL_MIN,
    FALL_SPEED_BASE,
    FALL_SPEED_MAX,
)

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import typing_game


class TypingGameTestCase(unittest.TestCase):
    def setUp(self):
        self.game = typing_game.TypingGame()
        self.game.state = self.game.STATE_PLAYING

    def test_get_difficulty_by_score(self):
        self.game.score = 0
        self.assertEqual(self.game.get_difficulty(), "easy")

        self.game.score = 100
        self.assertEqual(self.game.get_difficulty(), "medium")

        self.game.score = 300
        self.assertEqual(self.game.get_difficulty(), "hard")

    def test_spawn_interval_and_fall_speed_bounds(self):
        self.game.score = 0
        self.assertAlmostEqual(self.game.get_spawn_interval(), SPAWN_INTERVAL_BASE)
        self.assertAlmostEqual(self.game.get_fall_speed(), FALL_SPEED_BASE)

        self.game.score = 10_000
        self.assertAlmostEqual(self.game.get_spawn_interval(), SPAWN_INTERVAL_MIN)
        self.assertAlmostEqual(self.game.get_fall_speed(), FALL_SPEED_MAX)

    @patch("typing_game.random.randint", return_value=100)
    @patch("typing_game.random.uniform", return_value=0)
    @patch("typing_game.random.choice")
    def test_spawn_word_english(self, mock_choice, _mock_uniform, _mock_randint):
        self.game.mode = "english"
        self.game.score = 0

        mock_choice.side_effect = [typing_game.TEXT_YELLOW, "cat"]

        self.game.spawn_word()

        self.assertEqual(len(self.game.words), 1)
        word = self.game.words[0]
        self.assertEqual(word.display_text, "cat")
        self.assertEqual(word.type_text, "cat")
        self.assertEqual(word.speed, self.game.get_fall_speed())

    @patch("typing_game.random.randint", return_value=120)
    @patch("typing_game.random.uniform", return_value=0)
    @patch("typing_game.random.choice")
    def test_spawn_word_pinyin_strips_tone_digits(self, mock_choice, _mock_uniform, _mock_randint):
        self.game.mode = "pinyin"
        self.game.score = 0

        mock_choice.side_effect = [typing_game.TEXT_CYAN, ("雨", "yu2")]

        self.game.spawn_word()

        self.assertEqual(len(self.game.words), 1)
        word = self.game.words[0]
        self.assertEqual(word.display_text, "雨")
        self.assertEqual(word.type_text, "yu")

    def test_check_input_prefix_updates_matched_chars(self):
        word1 = typing_game.FallingWord("cat", "cat", 100, 0, typing_game.TEXT_WHITE)
        word2 = typing_game.FallingWord("dog", "dog", 200, 0, typing_game.TEXT_WHITE)
        self.game.words = [word1, word2]

        self.game.input_text = "c"
        self.game.check_input()

        self.assertEqual(word1.matched_chars, 1)
        self.assertEqual(word2.matched_chars, 0)

    def test_check_input_full_match_clears_word_and_resets_input(self):
        word = typing_game.FallingWord("cat", "cat", 100, 0, typing_game.TEXT_WHITE)
        self.game.words = [word]

        self.game.input_text = "cat"
        self.game.check_input()

        self.assertFalse(word.active)
        self.assertEqual(self.game.input_text, "")
        self.assertEqual(self.game.words_cleared, 1)
        self.assertGreater(self.game.score, 0)

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

    def test_check_input_multiple_words_shared_prefix_all_highlighted(self):
        word1 = typing_game.FallingWord("cat", "cat", 100, 0, typing_game.TEXT_WHITE)
        word2 = typing_game.FallingWord("car", "car", 200, 0, typing_game.TEXT_WHITE)
        word3 = typing_game.FallingWord("dog", "dog", 300, 0, typing_game.TEXT_WHITE)
        self.game.words = [word1, word2, word3]

        self.game.input_text = "ca"
        self.game.check_input()

        self.assertEqual(word1.matched_chars, 2)
        self.assertEqual(word2.matched_chars, 2)
        self.assertEqual(word3.matched_chars, 0)

    def test_check_input_multiple_words_backspace_recomputes_matches(self):
        word1 = typing_game.FallingWord("cat", "cat", 100, 0, typing_game.TEXT_WHITE)
        word2 = typing_game.FallingWord("car", "car", 200, 0, typing_game.TEXT_WHITE)
        self.game.words = [word1, word2]

        self.game.input_text = "ca"
        self.game.check_input()
        self.assertEqual(word1.matched_chars, 2)
        self.assertEqual(word2.matched_chars, 2)

        self.game.input_text = "c"
        self.game.check_input()

        self.assertEqual(word1.matched_chars, 1)
        self.assertEqual(word2.matched_chars, 1)

    def test_check_input_multiple_words_invalid_prefix_clears_all_matches(self):
        word1 = typing_game.FallingWord("cat", "cat", 100, 0, typing_game.TEXT_WHITE)
        word2 = typing_game.FallingWord("car", "car", 200, 0, typing_game.TEXT_WHITE)
        self.game.words = [word1, word2]

        self.game.input_text = "ca"
        self.game.check_input()
        self.assertEqual(word1.matched_chars, 2)
        self.assertEqual(word2.matched_chars, 2)

        self.game.input_text = "cz"
        self.game.check_input()

        self.assertEqual(word1.matched_chars, 0)
        self.assertEqual(word2.matched_chars, 0)

    def test_check_input_empty_input_clears_existing_match_state(self):
        word1 = typing_game.FallingWord("cat", "cat", 100, 0, typing_game.TEXT_WHITE)
        word2 = typing_game.FallingWord("car", "car", 200, 0, typing_game.TEXT_WHITE)
        self.game.words = [word1, word2]

        self.game.input_text = "ca"
        self.game.check_input()
        self.assertEqual(word1.matched_chars, 2)
        self.assertEqual(word2.matched_chars, 2)

        self.game.input_text = ""
        self.game.check_input()

        self.assertEqual(word1.matched_chars, 0)
        self.assertEqual(word2.matched_chars, 0)

    def test_check_input_duplicate_words_only_clears_one_per_submit(self):
        word1 = typing_game.FallingWord("cat", "cat", 100, 0, typing_game.TEXT_WHITE)
        word2 = typing_game.FallingWord("cat", "cat", 200, 0, typing_game.TEXT_WHITE)
        self.game.words = [word1, word2]

        self.game.input_text = "cat"
        self.game.check_input()

        self.assertFalse(word1.active)
        self.assertTrue(word2.active)
        self.assertEqual(self.game.words_cleared, 1)

    def test_check_input_ignores_inactive_word_even_if_prefix_matches(self):
        inactive_word = typing_game.FallingWord("cat", "cat", 100, 0, typing_game.TEXT_WHITE)
        active_word = typing_game.FallingWord("car", "car", 200, 0, typing_game.TEXT_WHITE)
        inactive_word.active = False
        self.game.words = [inactive_word, active_word]

        self.game.input_text = "ca"
        self.game.check_input()

        self.assertEqual(inactive_word.matched_chars, 0)
        self.assertEqual(active_word.matched_chars, 2)

    def test_check_input_case_insensitive_for_multiple_words(self):
        word1 = typing_game.FallingWord("Cat", "cat", 100, 0, typing_game.TEXT_WHITE)
        word2 = typing_game.FallingWord("Car", "car", 200, 0, typing_game.TEXT_WHITE)
        self.game.words = [word1, word2]

        self.game.input_text = "CA"
        self.game.check_input()

        self.assertEqual(word1.matched_chars, 2)
        self.assertEqual(word2.matched_chars, 2)

    def test_check_input_words_cat_are_job_with_caar_expected_020(self):
        word1 = typing_game.FallingWord("cat", "cat", 100, 0, typing_game.TEXT_WHITE)
        word2 = typing_game.FallingWord("are", "are", 200, 0, typing_game.TEXT_WHITE)
        word3 = typing_game.FallingWord("job", "job", 300, 0, typing_game.TEXT_WHITE)
        self.game.words = [word1, word2, word3]

        self.game.input_text = "caar"
        self.game.check_input()

        self.assertEqual(word1.matched_chars, 0)
        self.assertEqual(word2.matched_chars, 2)
        self.assertEqual(word3.matched_chars, 0)

    def test_check_input_words_cat_dog_append_clear_rules(self):
        def make_words():
            return [
                typing_game.FallingWord("cat", "cat", 100, 0, typing_game.TEXT_WHITE),
                typing_game.FallingWord("dog", "dog", 200, 0, typing_game.TEXT_WHITE),
                typing_game.FallingWord("append", "append", 300, 0, typing_game.TEXT_WHITE),
            ]

        self.game.words = make_words()
        self.game.input_text = "cat"
        self.game.check_input()
        self.assertFalse(self.game.words[0].active)
        self.assertTrue(self.game.words[1].active)
        self.assertTrue(self.game.words[2].active)

        self.game.words = make_words()
        self.game.input_text = "append"
        self.game.check_input()
        self.assertTrue(self.game.words[0].active)
        self.assertTrue(self.game.words[1].active)
        self.assertFalse(self.game.words[2].active)

        self.game.words = make_words()
        self.game.input_text = "cog"
        self.game.check_input()
        self.assertTrue(self.game.words[0].active)
        self.assertTrue(self.game.words[1].active)
        self.assertTrue(self.game.words[2].active)

        self.game.words = make_words()
        self.game.input_text = "incat"
        self.game.check_input()
        self.assertFalse(self.game.words[0].active)
        self.assertTrue(self.game.words[1].active)
        self.assertTrue(self.game.words[2].active)


if __name__ == "__main__":
    unittest.main(verbosity=2)
