from unittest.mock import patch

import typing_game
from test.common import TypingGameBaseTestCase


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
