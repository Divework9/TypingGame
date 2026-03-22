from unittest.mock import patch

from test.common import TypingGameBaseTestCase
import typing_game


class SpawnTestCase(TypingGameBaseTestCase):
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


    # R4-01: integration — spawn_word must pick from the correct difficulty tier
    def test_spawn_word_uses_easy_words_at_low_score(self):
        from conf.word_bank import ENGLISH_WORDS
        self.game.mode = "english"
        self.game.score = 0  # easy
        self.game.spawn_word()
        self.assertIn(self.game.words[-1].type_text, ENGLISH_WORDS["easy"])

    def test_spawn_word_uses_hard_words_at_high_score(self):
        from conf.word_bank import ENGLISH_WORDS
        self.game.mode = "english"
        self.game.score = 300  # hard
        self.game.spawn_word()
        self.assertIn(self.game.words[-1].type_text, ENGLISH_WORDS["hard"])

    def test_spawn_word_pinyin_uses_correct_tier(self):
        from conf.word_bank import PINYIN_WORDS
        self.game.mode = "pinyin"
        self.game.score = 100  # medium
        self.game.spawn_word()
        word = self.game.words[-1]
        medium_type_texts = [
            ''.join(c for c in pinyin if not c.isdigit())
            for _, pinyin in PINYIN_WORDS["medium"]
        ]
        self.assertIn(word.type_text, medium_type_texts)

class FallingWordTestCase(TypingGameBaseTestCase):
    def test_falling_word_update_moves_y_by_speed_times_dt(self):
        word = typing_game.FallingWord("cat", "cat", 100, 50.0, typing_game.TEXT_WHITE)
        initial_y = word.y  # starts at -30
        word.update(0.1)
        self.assertAlmostEqual(word.y, initial_y + 50.0 * 0.1)

    def test_falling_word_is_out_false_when_near_top(self):
        word = typing_game.FallingWord("cat", "cat", 100, 50.0, typing_game.TEXT_WHITE)
        # word.y starts at -30, nowhere near the bottom boundary
        self.assertFalse(word.is_out())

    def test_falling_word_is_out_true_when_past_boundary(self):
        word = typing_game.FallingWord("cat", "cat", 100, 0, typing_game.TEXT_WHITE)
        boundary = typing_game.SCREEN_H - (typing_game.BOTTOM_UI_HEIGHT + 15)
        word.y = boundary + 1
        self.assertTrue(word.is_out())

    def test_falling_word_is_out_false_at_exact_boundary(self):
        word = typing_game.FallingWord("cat", "cat", 100, 0, typing_game.TEXT_WHITE)
        boundary = typing_game.SCREEN_H - (typing_game.BOTTOM_UI_HEIGHT + 15)
        word.y = boundary  # exactly at boundary (not strictly greater)
        self.assertFalse(word.is_out())
