import pygame
import typing_game

from test.common import TypingGameBaseTestCase


class LetterStageInputTestCase(TypingGameBaseTestCase):
    def test_letter_mode_accepts_punctuation_in_current_stage(self):
        self.game.mode = "letter"
        self.game.letter_stage = 1

        event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_SEMICOLON, "unicode": ";"})
        self.game.handle_event(event)

        self.assertEqual(self.game.input_text, ";")

    def test_letter_mode_rejects_keys_outside_current_stage(self):
        self.game.mode = "letter"
        self.game.letter_stage = 1

        event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_q, "unicode": "q"})
        self.game.handle_event(event)

        self.assertEqual(self.game.input_text, "")

    def test_letter_mode_accepts_stage_three_dot(self):
        self.game.mode = "letter"
        self.game.letter_stage = 3

        event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_PERIOD, "unicode": "."})
        self.game.handle_event(event)

        self.assertEqual(self.game.input_text, ".")

    def test_letter_mode_wrong_key_not_on_screen_resets_combo(self):
        self.game.mode = "letter"
        self.game.letter_stage = 1
        self.game.combo = 6
        self.game.words = [
            typing_game.FallingWord("a", "a", 100, 0, typing_game.TEXT_WHITE),
        ]

        event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_s, "unicode": "s"})
        self.game.handle_event(event)

        self.assertEqual(self.game.combo, 0)
        self.assertEqual(self.game.input_text, "")
